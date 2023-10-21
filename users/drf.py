
from django.contrib.auth.models import User
from rest_framework import serializers, viewsets
from users.models import Profile

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'is_staff']


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


# -----------------------------------------------------------------------------


class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Profile
        # fields = ['user', 'status', 'is_alive', 'is_active', 'image', 'user_image']
        exclude = []

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer


# -----------------------------------------------------------------------------
