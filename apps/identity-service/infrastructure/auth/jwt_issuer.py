from __future__ import annotations

from datetime import datetime, timedelta, timezone
from functools import lru_cache
import hashlib
from pathlib import Path
import uuid
from typing import Any

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from django.conf import settings
import jwt

from infrastructure.auth.jwks import build_jwks


class TokenError(Exception):
    pass


@lru_cache(maxsize=1)
def get_signing_key_data() -> dict[str, str]:
    private_key_pem = _resolve_private_key()
    public_key_pem = _resolve_public_key(private_key_pem)
    kid = settings.JWT_KID or hashlib.sha256(public_key_pem.encode("utf-8")).hexdigest()[:16]
    return {
        "kid": kid,
        "private_key": private_key_pem,
        "public_key": public_key_pem,
    }


def _resolve_private_key() -> str:
    if settings.JWT_PRIVATE_KEY:
        return settings.JWT_PRIVATE_KEY

    if settings.JWT_PRIVATE_KEY_PATH:
        return Path(settings.JWT_PRIVATE_KEY_PATH).read_text()

    generated_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return generated_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8")


def _resolve_public_key(private_key_pem: str) -> str:
    if settings.JWT_PUBLIC_KEY:
        return settings.JWT_PUBLIC_KEY

    if settings.JWT_PUBLIC_KEY_PATH:
        return Path(settings.JWT_PUBLIC_KEY_PATH).read_text()

    private_key = serialization.load_pem_private_key(private_key_pem.encode("utf-8"), password=None)
    public_key = private_key.public_key()
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")


def issue_token(*, subject: str, token_type: str, expires_delta: timedelta, claims: dict[str, Any]) -> str:
    now = datetime.now(tz=timezone.utc)
    key_data = get_signing_key_data()
    payload = {
        "jti": str(uuid.uuid4()),
        "sub": subject,
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
        "token_type": token_type,
        **claims,
    }
    return jwt.encode(
        payload,
        key_data["private_key"],
        algorithm="RS256",
        headers={"kid": key_data["kid"], "typ": "JWT"},
    )


def verify_token(token: str, *, expected_token_type: str | None = None) -> dict[str, Any]:
    key_data = get_signing_key_data()
    try:
        payload = jwt.decode(
            token,
            key_data["public_key"],
            algorithms=["RS256"],
            issuer=settings.JWT_ISSUER,
            audience=settings.JWT_AUDIENCE,
        )
    except jwt.InvalidTokenError as exc:
        raise TokenError(str(exc)) from exc

    if expected_token_type and payload.get("token_type") != expected_token_type:
        raise TokenError(f"Invalid token type: expected {expected_token_type}")

    return payload


def get_public_key_pem() -> str:
    return get_signing_key_data()["public_key"]


def get_jwks_payload() -> dict[str, list[dict[str, Any]]]:
    key_data = get_signing_key_data()
    return build_jwks(public_key_pem=key_data["public_key"], kid=key_data["kid"])
