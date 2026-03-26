from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.organizations.selectors import list_memberships_for_user
from apps.organizations.serializers import MembershipSerializer

from .models import User
from .permissions import CanViewUserMemberships
from .serializers import CurrentUserSerializer


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = CurrentUserSerializer(request.user)
        return Response(serializer.data)


class UserMembershipListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, CanViewUserMemberships]
    serializer_class = MembershipSerializer

    def get_queryset(self):  
        user = get_object_or_404(User, id=self.kwargs["user_id"])
        return list_memberships_for_user(user)
