from django.db import models

from imaginarion.models import Picture
from rpg_project.utils import create_sorting_name


class KnowledgePacket(models.Model):
    title = models.CharField(max_length=100, unique=True)
    text = models.TextField()
    pictures = models.ManyToManyField(Picture, related_name='knowledge_packets', blank=True)
    sorting_name = models.CharField(max_length=250, blank=True, null=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.sorting_name = create_sorting_name(self.__str__())
        super(KnowledgePacket, self).save(*args, **kwargs)

    class Meta:
        ordering = ['title']
