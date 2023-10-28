from typing import List

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
