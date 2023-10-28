import strawberry
import strawberry_django

from users.models import User, Profile
from users.types import UserType, ProfileType

# if typing.TYPE_CHECKING:  # pragma: no cover
from typing import Any, List
from django.http import HttpRequest
from strawberry.types import Info


class IsAuthenticated(strawberry.BasePermission):
    message = 'User is not authenticated'

    def has_permission(self, source: 'Any', info: 'Info', **kwargs) -> bool:
        request: 'HttpRequest' = info.context['request']
        return request.user.is_authenticated


@strawberry.type
class Query:
    # unfilterable query
    users1: list[UserType] = strawberry_django.field(permission_classes=[IsAuthenticated])

    # filterable query
    @strawberry.field(permission_classes=[IsAuthenticated])
    def users2(self, id: int | None = None) -> List[UserType] | None:
        if id:
            return User.objects.filter(id=id)
        return User.objects.all()

    @strawberry.field(permission_classes=[IsAuthenticated])
    def profiles_by_user(self, info: "Info") -> list[ProfileType]:
        return Profile.objects.filter(user=info.context.request.user)


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
        username: str,
        first_name: str,
        last_name: str,
        email: str,
        is_superuser: bool,
        is_staff: bool,
        is_active: bool
    ) -> UserType:

        user = User.objects.get(id=id)
        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.is_superuser = is_superuser
        user.is_staff = is_staff
        user.is_active = is_active

        user.save()
        return user



schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
)