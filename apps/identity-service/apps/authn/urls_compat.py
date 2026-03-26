from django.urls import path

from .views import JwksView


urlpatterns = [
    path("", JwksView.as_view(), name="jwks-compat"),
]
