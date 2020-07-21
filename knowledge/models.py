from django.db import models

from imaginarion.models import Picture
from rpg_project.utils import create_sorting_name
from rules.models import Skill
from users.models import Profile


class KnowledgePacket(models.Model):
    title = models.CharField(max_length=100, unique=True)
    text = models.TextField()
    skills = models.ManyToManyField(
        to=Skill,
        related_name='knowledge_packets',
    )
    acquired_by = models.ManyToManyField(
        to=Profile,
        related_name='knowledge_packets',
        blank=True,
    )
    pictures = models.ManyToManyField(
        to=Picture,
        related_name='knowledge_packets',
        blank=True,
    )
    sorting_name = models.CharField(max_length=250, blank=True, null=True)

    class Meta:
        ordering = ['sorting_name']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.sorting_name = create_sorting_name(self.__str__())
        super().save(*args, **kwargs)
    
    def informables(self):
        qs = Profile.objects.filter(status__in=[
            'active_player',
        ])
        qs = qs.exclude(id__in=self.acquired_by.all())
        return qs
