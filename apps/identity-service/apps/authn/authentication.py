from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed

from apps.accounts.selectors import get_user_by_id
from infrastructure.auth.jwt_issuer import TokenError, verify_token


class JWTAuthentication(BaseAuthentication):
    keyword = b"bearer"

    def authenticate_header(self, request): 
        return "Bearer"

    def authenticate(self, request):
        auth = get_authorization_header(request).split()
        if not auth:
            return None
        if auth[0].lower() != self.keyword:
            return None
        if len(auth) != 2:
            raise AuthenticationFailed("Invalid Authorization header")

        token = auth[1].decode("utf-8")
        try:
            payload = verify_token(token, expected_token_type="access")
        except TokenError as exc:
            raise AuthenticationFailed(str(exc)) from exc

        user = get_user_by_id(payload.get("sub"))
        if not user or not user.is_active:
            raise AuthenticationFailed("User is inactive or missing")

        request.jwt_payload = payload
        return user, payload
