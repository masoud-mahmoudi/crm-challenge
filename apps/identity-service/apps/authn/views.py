from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from typing import cast

from infrastructure.auth.jwt_issuer import get_jwks_payload

from .serializers import LoginSerializer, RefreshSerializer, SignupSerializer
from .services import authenticate_user, issue_token_pair, refresh_access_token, register_user


class SignupView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = cast(dict[str, str], serializer.validated_data)
        user = register_user(
            email=payload["email"],
            password=payload["password"],
            full_name=payload["full_name"],
        )
        return Response(issue_token_pair(user), status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = cast(dict[str, str], serializer.validated_data)
        user = authenticate_user(email=payload["email"], password=payload["password"])
        return Response(issue_token_pair(user), status=status.HTTP_200_OK)


class RefreshView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = RefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = cast(dict[str, str], serializer.validated_data)
        return Response(refresh_access_token(refresh_token=payload["refresh_token"]), status=status.HTTP_200_OK)


class JwksView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        return Response(get_jwks_payload(), status=status.HTTP_200_OK)
