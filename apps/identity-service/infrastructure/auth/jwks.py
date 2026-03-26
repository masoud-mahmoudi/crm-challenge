import base64
from typing import Any

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


def _base64url_uint(value: int) -> str:
    raw = value.to_bytes((value.bit_length() + 7) // 8, "big")
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def build_jwk(public_key_pem: str, kid: str) -> dict[str, Any]:
    public_key = serialization.load_pem_public_key(public_key_pem.encode("utf-8"))
    if not isinstance(public_key, rsa.RSAPublicKey):
        raise TypeError("Only RSA public keys are supported")

    public_numbers = public_key.public_numbers()
    return {
        "kty": "RSA",
        "use": "sig",
        "alg": "RS256",
        "kid": kid,
        "n": _base64url_uint(public_numbers.n),
        "e": _base64url_uint(public_numbers.e),
    }


def build_jwks(public_key_pem: str, kid: str) -> dict[str, list[dict[str, Any]]]:
    return {"keys": [build_jwk(public_key_pem=public_key_pem, kid=kid)]}
