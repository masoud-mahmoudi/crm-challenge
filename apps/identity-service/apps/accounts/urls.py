from django.urls import path

from .views import MeView, UserMembershipListView


urlpatterns = [
    path("me/", MeView.as_view(), name="me"),
    path("<uuid:user_id>/memberships/", UserMembershipListView.as_view(), name="user-memberships"),
]
