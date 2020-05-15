from django.contrib.auth.models import User, Group
from rest_framework import viewsets, permissions
from vgg_food_vendor_project.food_vendor_app.serializers import UserSerialiser, GroupSerialiser


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerialiser
    permission_class = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerialiser
    permission_class = [permissions.IsAuthenticated]
