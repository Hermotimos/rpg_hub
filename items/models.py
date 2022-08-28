from django.core.validators import MinValueValidator
from django.db.models import (
    BooleanField,
    CharField,
    DecimalField,
    ForeignKey as FK,
    Model,
    PROTECT, SET_NULL,
    TextField,

)
from prosoponomikon.models import Character


class ItemCollection(Model):
    name = CharField(max_length=255)
    owner = FK(to=Character, related_name='collections', on_delete=PROTECT)

    class Meta:
        ordering = ['owner__fullname', 'name']

    def __str__(self):
        return f"{self.name} [{self.owner.fullname}]"


class Item(Model):
    name = CharField(max_length=255)
    info = TextField(blank=True, null=True)
    weight = DecimalField(
        max_digits=12, decimal_places=2, default=0,
        validators=[MinValueValidator(0)])
    collection = FK(
        to=ItemCollection, related_name='items',
        blank=True, null=True, on_delete=SET_NULL)
    is_deleted = BooleanField(default=False)

    class Meta:
        ordering = ['collection', 'name']

    def __str__(self):
        return self.name
