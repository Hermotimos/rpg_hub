from django.db import models

from rules.models import Klass
from users.models import Profile


class Achievement(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    profile = models.ForeignKey(
        to=Profile,
        related_name='achievements',
        on_delete=models.PROTECT,
    )
    
    def __str__(self):
        return self.name


class ProfileKlass(models.Model):
    profile = models.ForeignKey(
        to=Profile,
        related_name='profile_klasses',
        on_delete=models.PROTECT,
    )
    klass = models.ForeignKey(
        to=Klass,
        related_name='profile_klasses',
        on_delete=models.PROTECT,
    )
    title = models.CharField(max_length=200, blank=True, null=True)
    experience = models.PositiveSmallIntegerField()
    
    def __str__(self):
        return f'{self.profile.character_name}: {self.klass.name}'
    
    class Meta:
        ordering = ['profile__character_name']
        verbose_name = 'Profile Klass'
        verbose_name_plural = 'Profile Klasses'
    

class Level(models.Model):
    profile_klass = models.ForeignKey(
        to=ProfileKlass,
        related_name='levels',
        on_delete=models.CASCADE,
    )
    achievements = models.ManyToManyField(
        to=Achievement,
        related_name='levels',
        blank=True,
    )
    level_number = models.PositiveSmallIntegerField()
    level_mods = models.TextField()

    def __str__(self):
        return f'{self.profile_klass} [{self.klass.name}]'

    class Meta:
        ordering = ['profile_klass', 'level_number']

