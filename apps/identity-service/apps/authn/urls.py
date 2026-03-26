from django.urls import path

from .views import JwksView, LoginView, RefreshView, SignupView


urlpatterns = [
    path("signup/", SignupView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    path("refresh/", RefreshView.as_view(), name="refresh"),
    path("jwks/", JwksView.as_view(), name="jwks"),
]
