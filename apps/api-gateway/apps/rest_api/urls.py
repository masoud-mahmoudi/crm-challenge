from __future__ import annotations

from django.urls import path

from .views import HealthView, LoginView, LogoutView, MeView, RefreshView


urlpatterns = [
    path("health", HealthView.as_view(), name="health"),
    path("auth/login", LoginView.as_view(), name="auth-login"),
    path("auth/refresh", RefreshView.as_view(), name="auth-refresh"),
    path("auth/logout", LogoutView.as_view(), name="auth-logout"),
    path("auth/me", MeView.as_view(), name="auth-me"),
]