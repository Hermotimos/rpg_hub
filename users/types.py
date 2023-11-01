from typing import Optional

import strawberry

from prosoponomikon.models import Character
from users.models import Profile, User


@strawberry.django.type(User)
class UserType:
    id: int
    username: str
    first_name: str
    last_name: str
    email: str
    is_superuser: bool
    is_staff: bool
    is_active: bool
    profiles: list['ProfileType']


@strawberry.type
class ImageFieldType:
    """
    A custom type to reflect some of the Django's ImageField functionalities.
    """
    url: str
    width: Optional[int]
    height: Optional[int]

    @strawberry.field
    def url(self, info) -> Optional[str]:
        """
        In case of null image file return None to prevent exceptions:
        "ValueError: The 'image' attribute has no file associated with it".
        """
        try:
            return self.url
        except ValueError:
            return ''


@strawberry.django.type(Profile)
class ProfileType:
    id: int
    user: UserType
    status: str
    is_alive: bool
    is_active: bool
    image: ImageFieldType
    user_image: ImageFieldType
    character: Optional['CharacterType']

    # def resolve_user_image(self, info):
    #     return ImageFieldType(
    #         url=self.url,
    #         width=self.width,
    #         height=self.height,
    #     )


@strawberry.django.type(Character)
class CharacterType:
    id: int
    fullname: str
    profile: ProfileType
