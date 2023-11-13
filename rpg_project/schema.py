import strawberry
import strawberry_django

from users.models import User, Profile
from users.types import UserType, ProfileType
from communications.models import Statement, Thread
from communications.types import StatementType
from rpg_project.utils import clear_cache

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


# -----------------------------------------------------------------------------


@strawberry.type
class Query:
    # unfilterable query
    users1: list[UserType] = strawberry_django.field(permission_classes=permissions)
    profiles: list[ProfileType] = strawberry_django.field(permission_classes=permissions)
    statements_all: list[StatementType] = strawberry_django.field(permission_classes=permissions)

    # filterable query
    @strawberry.field(permission_classes=permissions)
    def users2(self, info: "Info", id: int | None = None) -> List[UserType] | None:
        if id:
            return User.objects.filter(id=id)
        return User.objects.all()

    @strawberry.field(permission_classes=permissions)
    def profiles_by_request_user(self, info: "Info") -> list[ProfileType]:
        return Profile.objects.filter(user=info.context.request.user)

    @strawberry.field(permission_classes=permissions)
    def profiles_by_user_id(self, info: "Info", user_id: int) -> list[ProfileType]:
        print(info.field_name)
        return Profile.objects.filter(user__id=user_id)

    @strawberry.field(permission_classes=permissions)
    def profiles_by_user_profile(self, info: "Info", profile_id: int) -> list[ProfileType]:
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

    @strawberry.field(permission_classes=permissions)
    def statements_by_thread_id(self, info: "Info", thread_id: int) -> list[StatementType]:
        statements = Statement.objects.filter(
            thread=thread_id
        ).order_by(
            'created_at'
        ).prefetch_related(
            'seen_by__character',
            'seen_by__user',
            'options',
            'thread__participants',
            'thread__followers',
            'thread__tags',
            'author__user',
            'author__character',
        )

        # A surrgoate solution for using request.current_profile, for learning.
        # This only works from within site; requests from Insomnia lack 'user'
        # which is ok, as they don't need to update seen_by field.
        user_id = info.context.request.user.id
        current_profile = Profile.objects.filter(user__id=user_id).order_by('status').first()
        thread = Thread.objects.get(id=thread_id)

        # Update all statements to be seen by the profile
        if (
            current_profile in thread.participants.all()
            or current_profile.status == 'gm'
        ):
            SeenBy = Statement.seen_by.through
            relations = []
            for statement in statements.exclude(seen_by=current_profile):
                relations.append(SeenBy(statement_id=statement.id, profile_id=current_profile.id))
            SeenBy.objects.bulk_create(relations, ignore_conflicts=True)

            # If SeenBy has been changed, clear appropriate cache for the user
            # bulk_create() doesn't use model's save()  so no signals are fired
            # https://docs.djangoproject.com/en/4.2/ref/models/querysets/#bulk-create
            if relations:
                if thread.kind == 'Announcement':
                    clear_cache(cachename='navbar', vary_on_list=[[current_profile.user.id]])
                elif thread.kind == 'Debate':
                    clear_cache(cachename='sidebar', vary_on_list=[[current_profile.user.id]])

        return statements


# -----------------------------------------------------------------------------


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


# -----------------------------------------------------------------------------


schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
)