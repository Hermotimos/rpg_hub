from django.db import models

from imaginarion.models import Picture
from rules.models import SkillLevel
from users.models import Profile


class Character(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    skill_levels_acquired = models.ManyToManyField(SkillLevel, related_name='acquired_by_characters', blank=True)
    pictures = models.ManyToManyField(Picture, related_name='characters_pics', blank=True)

    def __str__(self):
        return f'{self.profile.character_name}'

    class Meta:
        ordering = ['profile']
