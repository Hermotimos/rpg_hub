import strawberry

from communications import models
from users.types import ProfileType, ImageFieldType


@strawberry.django.type(models.Thread)
class ThreadType:
    id: int
    title: str
    kind: str
    participants: list[ProfileType]
    followers: list[ProfileType]
    # tags: ...
    is_ended: bool
    is_exclusive: bool
    created_at: str


@strawberry.django.type(models.Statement)
class StatementType:
    id: int
    text: str
    thread: ThreadType
    author: ProfileType
    image: ImageFieldType
    seen_by: list[ProfileType]
    created_at: str

    @strawberry.field
    def created_datetime(self) -> str:
        """Additional field for formatted value of 'created_at' field."""
        return self.created_at.strftime('%Y-%m-%d | %H:%M')
