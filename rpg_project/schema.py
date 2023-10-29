import strawberry
import strawberry_django

from users.models import User, Profile
from users.types import UserType, ProfileType

# if typing.TYPE_CHECKING:  # pragma: no cover
from typing import Any, List
from django.http import HttpRequest
from django.conf import settings
from strawberry.types import Info


class IsAuthenticated(strawberry.BasePermission):
    message = 'User is not authenticated'

    def has_permission(self, source: 'Any', info: 'Info', **kwargs) -> bool:
        request: 'HttpRequest' = info.context['request']
        return request.user.is_authenticated

if settings.IS_LOCAL_ENVIRON:
    permissions = None
else:
    permissions = [IsAuthenticated]

@strawberry.type
class Query:
    # unfilterable query
    users1: list[UserType] = strawberry_django.field(permission_classes=permissions)
    profiles: list[ProfileType] = strawberry_django.field(permission_classes=permissions)

    # filterable query
    @strawberry.field(permission_classes=permissions)
    def users2(self, id: int | None = None) -> List[UserType] | None:
        if id:
            return User.objects.filter(id=id)
        return User.objects.all()

    @strawberry.field(permission_classes=permissions)
    def profiles_by_request_user(self, info: "Info") -> list[ProfileType]:
        return Profile.objects.filter(user=info.context.request.user)

    @strawberry.field(permission_classes=permissions)
    def profiles_by_user_id(self, user_id: int) -> list[ProfileType]:
        return Profile.objects.filter(user__id=user_id)

    @strawberry.field(permission_classes=permissions)
    def profiles_by_user_profile(self, profile_id: int) -> list[ProfileType]:
        """
        This query achieves current_profile.user.get_all_user_profiles()
        query MyQuery {
            profileUserProfiles(profileId: 11) {
                image
                status
                user {
                    username
                }
            }
        }
        """
        profile = Profile.objects.get(id=profile_id)
        return Profile.objects.filter(user__id=profile.user.id).order_by('status')


@strawberry.type
class Mutation:

    @strawberry.field
    def create_user(
        self,
        username: str,
        first_name: str = '',
        last_name: str = '',
        email: str | None = None,
        is_superuser: bool = False,
        is_staff: bool = False,
        is_active: bool = False
    ) -> UserType:

        user = User(
            username=username, first_name=first_name, last_name=last_name,
            email=email, is_superuser=is_superuser, is_staff=is_staff,
            is_active=is_active)

        user.save()
        return user


    @strawberry.field
    def update_user(
        self,
        id: int,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        email: str | None = None,
        is_superuser: bool | None = None,
        is_staff: bool | None = None,
        is_active: bool | None = None
    ) -> UserType:

        user = User.objects.get(id=id)
        user.username = username or user.username
        user.first_name = first_name or user.first_name
        user.last_name = last_name or user.last_name
        user.email = email or user.email
        user.is_superuser = is_superuser or user.is_superuser
        user.is_staff = is_staff or user.is_staff
        user.is_active = is_active or user.is_active

        user.save()
        return user

    @strawberry.field
    def delete_user(
        self,
        id: int,
    ) -> str:

        try:
            user = User.objects.get(id=id)
            user.delete()
            return 'User deleted.'
        except User.DoesNotExist:
            return 'User matching query does not exist.'



schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
)