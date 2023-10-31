import strawberry

from users.models import User, Profile
from prosoponomikon.models import Character


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
class ImageField:
    """
    A custom type to reflect some of the Django's ImageField functionalities.
    """
    url: str
    width: int
    height: int


@strawberry.django.type(Profile)
class ProfileType:
    id: int
    user: UserType
    status: str
    is_alive: bool
    is_active: bool
    image: ImageField
    user_image: ImageField
    character: 'CharacterType'

    # def resolve_user_image(self, info):
    #     return ImageField(
    #         url=self.url,
    #         width=self.width,
    #         height=self.height,
    #     )


@strawberry.django.type(Character)
class CharacterType:
    id: int
    fullname: str
    profile: ProfileType
