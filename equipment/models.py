from django.db import models

from toponomikon.models import SecondaryLocation
from users.models import Profile


class ItemStorage(models.Model):
    name = models.CharField(max_length=250)
    description = models.TextField()
    owners = models.ManyToManyField(
        to=Profile,
        related_name='item_storages',
    )
    location = models.ForeignKey(
        to=SecondaryLocation,
        related_name='item_storages',
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    
    def __str__(self):
        return f'{self.name}: {", ".join([o for o in self.owners.all()])}'

    class Meta:
        ordering = ['name']
        
        
class Item(models.Model):
    name = models.CharField(max_length=250)
    description = models.TextField()
    amount = models.PositiveSmallIntegerField(default=1)
    weight = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    storage = models.ForeignKey(
        to=ItemStorage,
        related_name='items',
        on_delete=models.CASCADE,
    )
    
    def __str__(self):
        return f'{self.name} [{self.storage.name}]'
    
    class Meta:
        ordering = ['name']
