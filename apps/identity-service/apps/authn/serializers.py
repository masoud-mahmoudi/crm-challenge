from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(trim_whitespace=False)


class SignupSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(trim_whitespace=False, min_length=8)
    full_name = serializers.CharField(max_length=255)


class RefreshSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(trim_whitespace=False)
