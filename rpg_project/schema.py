import strawberry

from users.models import User
from users.types import UserType
from typing import List


@strawberry.type
class Query:

    @strawberry.field
    def users(self, id: int |None = None) -> List[UserType]:
        if id:
            return User.objects.filter(id=id)
        return User.objects.all()



@strawberry.type
class Mutation:

    @strawberry.field
    def create_user(
        self,
        username: str,
        first_name: str,
        last_name: str,
        is_superuser: bool,
        is_staff: bool,
        is_active: bool
    ) -> UserType:

        user = User(
            username=username, first_name=first_name, last_name=last_name,
            is_superuser=is_superuser, is_staff=is_staff, is_active=is_active)

        user.save()
        return user


    @strawberry.field
    def update_user(
        self,
        id: int,
        username: str,
        first_name: str,
        last_name: str,
        is_superuser: bool,
        is_staff: bool,
        is_active: bool
    ) -> UserType:

        user = User.objects.get(id=id)
        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        user.is_superuser = is_superuser
        user.is_staff = is_staff
        user.is_active = is_active

        user.save()
        return user





schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
)