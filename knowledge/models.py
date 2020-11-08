from django.db.models import (
    CharField,
    ForeignKey,
    ManyToManyField as M2MField,
    Model,
    PROTECT,
    TextField,
)

from imaginarion.models import Picture
from rpg_project.utils import create_sorting_name
from rules.models import Skill
from users.models import Profile


class KnowledgePacket(Model):
    title = CharField(max_length=100, unique=True)
    text = TextField()
    skills = M2MField(to=Skill, related_name='knowledge_packets')
    acquired_by = M2MField(to=Profile, related_name='knowledge_packets', blank=True)
    pictures = M2MField(to=Picture, related_name='knowledge_packets', blank=True)
    sorting_name = CharField(max_length=250, blank=True, null=True)

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


class PlayerKnowledgePacket(KnowledgePacket):
    author = ForeignKey(
        to=Profile,
        related_name='authored_kn_packets',
        on_delete=PROTECT,
    )
    

class MapPacket(Model):
    title = CharField(max_length=100, unique=True)
    acquired_by = M2MField(to=Profile, related_name='map_packets', blank=True)
    pictures = M2MField(to=Picture, related_name='map_packets')
    sorting_name = CharField(max_length=250, blank=True, null=True)

    class Meta:
        ordering = ['sorting_name']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.sorting_name = create_sorting_name(self.__str__())
        super().save(*args, **kwargs)