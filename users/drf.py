
from django.contrib.auth.models import User, Group
from rest_framework import serializers, viewsets
from rest_framework import permissions
from users.models import Profile


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


# -----------------------------------------------------------------------------


class ProfileSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Profile
        # fields = ['user', 'status', 'is_alive', 'is_active', 'image', 'user_image']
        exclude = []


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]


# -----------------------------------------------------------------------------


class UserSerializer(serializers.HyperlinkedModelSerializer):
    # Additional field for reverse relationship, must be included in Meta.fields
    # Other options: serializers.StringRelatedField, serializers.PrimaryKeyRelatedField
    # view_name='profile-detail': default as per ModelViewSet
    profiles = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='profile-detail')

    class Meta:
        model = User
        fields = ['id', 'url', 'username', 'email', 'is_staff', 'profiles']


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


# -----------------------------------------------------------------------------
