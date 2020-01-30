from django.db import models

from knowledge.models import KnowledgePacket
from imaginarion.models import Picture
from rules.models import SkillLevel, SynergyLevel
from users.models import Profile


class Character(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    skill_levels_acquired = models.ManyToManyField(SkillLevel, related_name='acquired_by_characters', blank=True)
    synergy_levels_acquired = models.ManyToManyField(SynergyLevel, related_name='acquired_by_characters', blank=True)
    knowledge_packets = models.ManyToManyField(KnowledgePacket, related_name='characters', blank=True)
    pictures = models.ManyToManyField(Picture, related_name='characters_pics', blank=True)

    def __str__(self):
        return f'{self.profile.character_name}'

    class Meta:
        ordering = ['profile']
