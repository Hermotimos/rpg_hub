import strawberry

from users import models


@strawberry.django.type(models.User)
class UserType:
    id: int
    username: str
    first_name: str
    last_name: str
    email: str
    is_superuser: bool
    is_staff: bool
    is_active: bool


@strawberry.django.type(models.Profile)
class ProfileType:
    id: int
    user: UserType
    status: str
    is_alive: bool
    is_active: bool
    image: str
