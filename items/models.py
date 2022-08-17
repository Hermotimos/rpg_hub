from django.core.validators import MinValueValidator
from django.db.models import (
    CASCADE,
    CharField,
    DecimalField,
    ForeignKey as FK,
    Model,
    TextField,

)
from prosoponomikon.models import Character


class Collection(Model):
    COLLECTION_TYPES = [
        ('Ekwipunek', 'Ekwipunek'),
        ('Depozyt/Skrytka', 'Depozyt/Skrytka'),
        ('Zwierzę juczne/Tragarz', 'Zwierzę juczne/Tragarz'),
    ]
    name = CharField(max_length=255)
    info = TextField(blank=True, null=True)
    owner = FK(to=Character, related_name='collections', on_delete=CASCADE)
    type = CharField(max_length=50, choices=COLLECTION_TYPES)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"[{self.owner.fullname}] {self.name}"
    
    # @property TODO annotate sum
    # def weight(self):
    #     return sum(item.weight for item in self.items.all())
    

class Item(Model):
    name = CharField(max_length=255)
    info = TextField(blank=True, null=True)
    collection = FK(to=Collection, related_name='items', on_delete=CASCADE)
    weight = DecimalField(
        max_digits=12, decimal_places=2, default=0,
        validators=[MinValueValidator(0)])
    
    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} [{self.collection}]"
