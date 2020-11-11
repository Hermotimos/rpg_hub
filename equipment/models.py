from django.db.models import (
    CharField,
    CASCADE,
    DecimalField,
    ForeignKey as FK,
    ManyToManyField as M2MField,
    Model,
    PositiveSmallIntegerField,
    PROTECT,
    TextField,
)

from toponomikon.models import SecondaryLocation
from users.models import Profile


class ItemStorage(Model):
    name = CharField(max_length=250)
    description = TextField()
    owners = M2MField(to=Profile, related_name='item_storages')
    location = FK(
        to=SecondaryLocation,
        related_name='item_storages',
        on_delete=PROTECT,
        blank=True,
        null=True,
    )
    
    def __str__(self):
        return f'{self.name}: {", ".join([o for o in self.owners.all()])}'

    class Meta:
        ordering = ['name']
        
        
class Item(Model):
    name = CharField(max_length=250)
    description = TextField()
    amount = PositiveSmallIntegerField(default=1)
    weight = DecimalField(max_digits=10, decimal_places=2, default=0)
    storage = FK(to=ItemStorage, related_name='items', on_delete=CASCADE)
    
    def __str__(self):
        return f'{self.name} [{self.storage.name}]'
    
    class Meta:
        ordering = ['name']
