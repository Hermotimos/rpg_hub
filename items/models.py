from django.core.validators import MinValueValidator
from django.db.models import (
    CharField,
    DecimalField,
    ForeignKey as FK,
    Model,
    PROTECT,
    TextField,

)
from prosoponomikon.models import Character


class Item(Model):
    COLLECTION_TYPES = [
        ('Osobisty', 'Osobisty'),
        ('Bagaż', 'Bagaż'),
        ('Depozyt', 'Depozyt'),
        ('Skrytka', 'Skrytka'),
        ('Koń/Muł', 'Koń/Muł'),
        ('Tragarz', 'Tragarz'),
    ]
    name = CharField(max_length=255)
    info = TextField(blank=True, null=True)
    weight = DecimalField(
        max_digits=12, decimal_places=2, default=0,
        validators=[MinValueValidator(0)])
    owner = FK(to=Character, related_name='items', on_delete=PROTECT)
    type = CharField(max_length=255, choices=COLLECTION_TYPES)

    class Meta:
        ordering = ['owner', 'type', 'name']

    def __str__(self):
        return f"{self.name} [{self.owner.fullname}: {self.type}]"
