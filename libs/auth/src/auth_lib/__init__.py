from __future__ import annotations

import base64
import os
import time
import uuid
from dataclasses import dataclass, field
from functools import wraps
from typing import Any, Iterable, Mapping, MutableMapping, Sequence

from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse
import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


DEFAULT_ALGORITHM = "RS256"
DEFAULT_JWKS_CACHE_SECONDS = 300
_JWKS_CLIENTS: MutableMapping[str, tuple[float, jwt.PyJWKClient]] = {}


class AuthError(Exception):
    def __init__(self, message: str, status_code: int = 401):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


@dataclass(frozen=True)
class MembershipScope:
    company_id: str
    company_name: str | None = None
    company_type: str | None = None
    parent_company_id: str | None = None
    role: str | None = None

    @classmethod
    def from_claim(cls, claim: Mapping[str, Any]) -> "MembershipScope":
        company_id = str(claim.get("company_id") or "").strip()
        if not company_id:
            raise AuthError("Membership claims must include company_id", status_code=401)

        return cls(
            company_id=company_id,
            company_name=str(claim.get("company_name")) if claim.get("company_name") else None,
            company_type=str(claim.get("company_type")) if claim.get("company_type") else None,
            parent_company_id=str(claim.get("parent_company_id")) if claim.get("parent_company_id") else None,
            role=str(claim.get("role")) if claim.get("role") else None,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "company_id": self.company_id,
            "company_name": self.company_name,
            "company_type": self.company_type,
            "parent_company_id": self.parent_company_id,
            "role": self.role,
        }


@dataclass(frozen=True)
class TenantAccess:
    membership_company_ids: Sequence[str] = field(default_factory=tuple)
    visible_company_ids: Sequence[str] = field(default_factory=tuple)
    data_company_ids: Sequence[str] = field(default_factory=tuple)
    parent_company_ids: Sequence[str] = field(default_factory=tuple)
    default_company_id: str | None = None

    @classmethod
    def from_claims(
        cls,
        claims: Mapping[str, Any],
        memberships: Sequence[MembershipScope],
    ) -> "TenantAccess":
        tenant_access = claims.get("tenant_access")
        if isinstance(tenant_access, Mapping):
            membership_company_ids = _normalize_company_ids(tenant_access.get("membership_company_ids"))
            visible_company_ids = _normalize_company_ids(tenant_access.get("visible_company_ids"))
            data_company_ids = _normalize_company_ids(tenant_access.get("data_company_ids"))
            parent_company_ids = _normalize_company_ids(tenant_access.get("parent_company_ids"))
            default_company_id = str(tenant_access.get("default_company_id")) if tenant_access.get("default_company_id") else None
        else:
            membership_company_ids = tuple(sorted({membership.company_id for membership in memberships}))
            visible_company_ids = membership_company_ids
            data_company_ids = tuple(
                sorted({membership.company_id for membership in memberships if membership.company_type != "PARENT"})
            )
            parent_company_ids = tuple(
                sorted({membership.company_id for membership in memberships if membership.company_type == "PARENT"})
            )
            default_company_id = data_company_ids[0] if data_company_ids else (visible_company_ids[0] if visible_company_ids else None)

        if not visible_company_ids and membership_company_ids:
            visible_company_ids = membership_company_ids
        if not data_company_ids:
            data_company_ids = tuple(
                company_id for company_id in visible_company_ids if company_id not in set(parent_company_ids)
            )

        return cls(
            membership_company_ids=membership_company_ids,
            visible_company_ids=visible_company_ids,
            data_company_ids=data_company_ids,
            parent_company_ids=parent_company_ids,
            default_company_id=default_company_id,
        )

    def can_access_company(self, company_id: str, *, data_scope: bool = True) -> bool:
        normalized_company_id = str(company_id).strip()
        allowed_company_ids = self.data_company_ids if data_scope else self.visible_company_ids
        return normalized_company_id in set(allowed_company_ids)

    def require_company_access(self, company_id: str, *, data_scope: bool = True) -> str:
        normalized_company_id = str(company_id).strip()
        if not normalized_company_id:
            raise AuthError("company_id is required for tenant-scoped access", status_code=403)
        if not self.can_access_company(normalized_company_id, data_scope=data_scope):
            raise AuthError(
                f"Not authorized for company_id '{normalized_company_id}'",
                status_code=403,
            )
        return normalized_company_id

    def to_dict(self) -> dict[str, Any]:
        return {
            "membership_company_ids": list(self.membership_company_ids),
            "visible_company_ids": list(self.visible_company_ids),
            "data_company_ids": list(self.data_company_ids),
            "parent_company_ids": list(self.parent_company_ids),
            "default_company_id": self.default_company_id,
        }


@dataclass(frozen=True)
class AuthContext:
    token: str
    claims: Mapping[str, Any]
    subject: str | None
    email: str | None
    roles: Sequence[str]
    memberships: Sequence[MembershipScope] = field(default_factory=tuple)
    tenant_access: TenantAccess = field(default_factory=TenantAccess)

    @property
    def user_id(self) -> str | None:
        return self.subject

    @property
    def is_authenticated(self) -> bool:
        return bool(self.token and self.subject)

    def can_access_company(self, company_id: str, *, data_scope: bool = True) -> bool:
        return self.tenant_access.can_access_company(company_id, data_scope=data_scope)

    def require_company_access(self, company_id: str, *, data_scope: bool = True) -> str:
        return self.tenant_access.require_company_access(company_id, data_scope=data_scope)

    def to_dict(self) -> dict[str, Any]:
        return {
            "authenticated": self.is_authenticated,
            "subject": self.subject,
            "user_id": self.user_id,
            "email": self.email,
            "roles": list(self.roles),
            "memberships": [membership.to_dict() for membership in self.memberships],
            "tenant_access": self.tenant_access.to_dict(),
            "claims": dict(self.claims),
        }


def _normalize_company_ids(value: Any) -> tuple[str, ...]:
    if not isinstance(value, Iterable) or isinstance(value, (str, bytes, Mapping)):
        return tuple()
    return tuple(sorted({str(item).strip() for item in value if str(item).strip()}))


def _parse_membership_claims(claims: Mapping[str, Any]) -> tuple[MembershipScope, ...]:
    raw_memberships = claims.get("memberships")
    if not isinstance(raw_memberships, list):
        return tuple()

    memberships: list[MembershipScope] = []
    for raw_membership in raw_memberships:
        if isinstance(raw_membership, Mapping):
            memberships.append(MembershipScope.from_claim(raw_membership))
    return tuple(memberships)


def _base64url_uint(value: int) -> str:
    raw = value.to_bytes((value.bit_length() + 7) // 8, "big")
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def generate_rsa_key_pair(kid: str | None = None) -> dict[str, Any]:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    key_id = kid or uuid.uuid4().hex

    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8")
    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")

    public_numbers = public_key.public_numbers()

    return {
        "kid": key_id,
        "algorithm": DEFAULT_ALGORITHM,
        "created_at": int(time.time()),
        "private_key_pem": private_key_pem,
        "public_key_pem": public_key_pem,
        "jwk": {
            "kty": "RSA",
            "use": "sig",
            "kid": key_id,
            "alg": DEFAULT_ALGORITHM,
            "n": _base64url_uint(public_numbers.n),
            "e": _base64url_uint(public_numbers.e),
        },
    }


def issue_jwt(
    *,
    private_key_pem: str,
    kid: str,
    issuer: str,
    audience: str,
    subject: str,
    claims: Mapping[str, Any] | None = None,
    lifetime_seconds: int = 3600,
) -> str:
    now = int(time.time())
    payload = {
        "iss": issuer,
        "aud": audience,
        "sub": subject,
        "iat": now,
        "exp": now + lifetime_seconds,
        **(dict(claims or {})),
    }
    return jwt.encode(
        payload,
        private_key_pem,
        algorithm=DEFAULT_ALGORITHM,
        headers={"kid": kid, "typ": "JWT"},
    )


def read_bearer_token(headers: Mapping[str, Any]) -> str:
    authorization = headers.get("Authorization") or headers.get("authorization")
    if not authorization:
        raise AuthError("Missing Authorization header", status_code=401)

    scheme, _, token = str(authorization).partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        raise AuthError("Authorization header must use Bearer token", status_code=401)

    return token.strip()


def _get_jwks_client(jwks_url: str, cache_seconds: int = DEFAULT_JWKS_CACHE_SECONDS) -> jwt.PyJWKClient:
    now = time.time()
    cached = _JWKS_CLIENTS.get(jwks_url)
    if cached and now - cached[0] < cache_seconds:
        return cached[1]

    client = jwt.PyJWKClient(jwks_url)
    _JWKS_CLIENTS[jwks_url] = (now, client)
    return client


def verify_jwt(
    token: str,
    *,
    jwks_url: str,
    issuer: str,
    audience: str,
    algorithms: Sequence[str] = (DEFAULT_ALGORITHM,),
) -> dict[str, Any]:
    try:
        signing_key = _get_jwks_client(jwks_url).get_signing_key_from_jwt(token)
        return jwt.decode(
            token,
            signing_key.key,
            algorithms=list(algorithms),
            issuer=issuer,
            audience=audience,
        )
    except jwt.ExpiredSignatureError as exc:
        raise AuthError("Token has expired", status_code=401) from exc
    except jwt.InvalidTokenError as exc:
        raise AuthError(f"Invalid token: {exc}", status_code=401) from exc


def build_auth_context(
    headers: Mapping[str, Any],
    *,
    jwks_url: str,
    issuer: str,
    audience: str,
) -> AuthContext:
    token = read_bearer_token(headers)
    claims = verify_jwt(
        token,
        jwks_url=jwks_url,
        issuer=issuer,
        audience=audience,
    )
    roles = claims.get("roles") or []
    if not isinstance(roles, list):
        roles = [str(roles)]
    memberships = _parse_membership_claims(claims)
    tenant_access = TenantAccess.from_claims(claims, memberships)

    return AuthContext(
        token=token,
        claims=claims,
        subject=claims.get("sub"),
        email=claims.get("email"),
        roles=[str(role) for role in roles],
        memberships=memberships,
        tenant_access=tenant_access,
    )


def authorize_company_access(
    auth_context: AuthContext,
    company_id: str,
    *,
    data_scope: bool = True,
) -> str:
    return auth_context.require_company_access(company_id, data_scope=data_scope)


def get_record_company_id(record: Any, company_id_field: str = "company_id") -> str:
    if isinstance(record, Mapping):
        value = record.get(company_id_field)
    else:
        value = getattr(record, company_id_field, None)

    normalized_company_id = str(value).strip() if value is not None else ""
    if not normalized_company_id:
        raise AuthError(
            f"Tenant-scoped records must expose '{company_id_field}'",
            status_code=500,
        )
    return normalized_company_id


def is_record_authorized(
    auth_context: AuthContext,
    record: Any,
    *,
    company_id_field: str = "company_id",
    data_scope: bool = True,
) -> bool:
    return auth_context.can_access_company(
        get_record_company_id(record, company_id_field=company_id_field),
        data_scope=data_scope,
    )


def filter_authorized_records(
    auth_context: AuthContext,
    records: Iterable[Any],
    *,
    company_id_field: str = "company_id",
    data_scope: bool = True,
) -> list[Any]:
    return [
        record
        for record in records
        if is_record_authorized(
            auth_context,
            record,
            company_id_field=company_id_field,
            data_scope=data_scope,
        )
    ]


def get_django_auth_settings() -> dict[str, str]:
    jwks_url = getattr(
        settings,
        "JWT_JWKS_URL",
        getattr(settings, "JWKS_URL", os.getenv("JWT_JWKS_URL", os.getenv("JWKS_URL", ""))),
    ).strip()
    issuer = getattr(
        settings,
        "JWT_ISSUER",
        os.getenv("JWT_ISSUER", "https://identity.aerolytic.local"),
    ).strip()
    audience = getattr(
        settings,
        "JWT_AUDIENCE",
        os.getenv("JWT_AUDIENCE", "aerolytic-clients"),
    ).strip()

    if not jwks_url:
        raise AuthError("JWKS_URL is not configured", status_code=500)

    return {
        "jwks_url": jwks_url,
        "issuer": issuer,
        "audience": audience,
    }


def attach_auth_context(
    request: HttpRequest,
    *,
    jwks_url: str | None = None,
    issuer: str | None = None,
    audience: str | None = None,
) -> AuthContext:
    resolved = {
        **get_django_auth_settings(),
        **{
            key: value
            for key, value in {
                "jwks_url": jwks_url,
                "issuer": issuer,
                "audience": audience,
            }.items()
            if value
        },
    }
    auth_context = build_auth_context(
        request.headers,
        jwks_url=resolved["jwks_url"],
        issuer=resolved["issuer"],
        audience=resolved["audience"],
    )
    setattr(request, "auth_context", auth_context)
    return auth_context


def require_auth(view_func):
    @wraps(view_func)
    def wrapped(request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        try:
            attach_auth_context(request)
        except AuthError as exc:
            return JsonResponse({"error": exc.message}, status=exc.status_code)

        return view_func(request, *args, **kwargs)

    return wrapped


class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        setattr(request, "auth_context", None)

        if request.headers.get("Authorization"):
            try:
                attach_auth_context(request)
            except AuthError as exc:
                return JsonResponse({"error": exc.message}, status=exc.status_code)

        return self.get_response(request)


def validate_token(token: str) -> bool:
    resolved = get_django_auth_settings()
    verify_jwt(
        token,
        jwks_url=resolved["jwks_url"],
        issuer=resolved["issuer"],
        audience=resolved["audience"],
    )
    return True


__all__ = [
    "AuthContext",
    "AuthError",
    "DEFAULT_ALGORITHM",
    "JWTAuthenticationMiddleware",
    "MembershipScope",
    "TenantAccess",
    "attach_auth_context",
    "authorize_company_access",
    "build_auth_context",
    "filter_authorized_records",
    "generate_rsa_key_pair",
    "get_django_auth_settings",
    "get_record_company_id",
    "is_record_authorized",
    "issue_jwt",
    "read_bearer_token",
    "require_auth",
    "validate_token",
    "verify_jwt",
]