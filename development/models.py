from django.db.models import (
    CharField,
    CASCADE,
    ForeignKey as FK,
    ManyToManyField as M2MField,
    Model,
    PositiveSmallIntegerField,
    PROTECT,
    TextField,
)

from rules.models import Klass
from users.models import Profile


class Achievement(Model):
    name = CharField(max_length=100)
    description = TextField()
    profile = FK(to=Profile, related_name='achievements', on_delete=PROTECT)
    
    def __str__(self):
        return self.name


class ProfileKlass(Model):
    profile = FK(to=Profile, related_name='profile_klasses', on_delete=PROTECT)
    klass = FK(to=Klass, related_name='profile_klasses', on_delete=PROTECT)
    title = CharField(max_length=200, blank=True, null=True)
    experience = PositiveSmallIntegerField()
    
    def __str__(self):
        return f'{self.profile.character_name}: {self.klass.name}'
    
    class Meta:
        ordering = ['profile__character_name']
        verbose_name = 'Profile Klass'
        verbose_name_plural = 'Profile Klasses'
    

class Level(Model):
    profile_klass = FK(to=ProfileKlass, related_name='levels', on_delete=CASCADE)
    achievements = M2MField(to=Achievement, related_name='levels', blank=True)
    level_number = PositiveSmallIntegerField()
    level_mods = TextField()

    def __str__(self):
        return f'{self.profile_klass} [{self.klass.name}]'

    class Meta:
        ordering = ['profile_klass', 'level_number']
