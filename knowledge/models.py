from django.db.models import (
    CASCADE,
    CharField,
    ForeignKey as FK,
    ManyToManyField as M2M,
    Model,
    PROTECT,
    TextField,
)

from imaginarion.models import Picture
from rpg_project.utils import create_sorting_name
from rules.models import Skill
from users.models import Profile


class InfoPacket(Model):
    title = CharField(max_length=100, unique=True)
    text = TextField(blank=True, null=True)
    sorting_name = CharField(max_length=250, blank=True, null=True)

    class Meta:
        abstract = True
        ordering = ['sorting_name']
        

class DialoguePacket(InfoPacket):
    pass
    
        
class KnowledgePacket(InfoPacket):
    author = FK(
        to=Profile,
        related_name='authored_kn_packets',
        on_delete=PROTECT,
        null=True,
        blank=True,
    )
    acquired_by = M2M(to=Profile, related_name='knowledge_packets', blank=True)
    pictures = M2M(to=Picture, related_name='knowledge_packets', blank=True)
    skills = M2M(to=Skill, related_name='knowledge_packets')

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
    

class MapPacket(InfoPacket):
    acquired_by = M2M(to=Profile, related_name='map_packets', blank=True)
    pictures = M2M(to=Picture, related_name='map_packets')

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.sorting_name = create_sorting_name(self.__str__())
        super().save(*args, **kwargs)


class BiographyPacket(InfoPacket):
    author = FK(
        to=Profile,
        related_name='authored_bio_packets',
        on_delete=PROTECT,
        null=True,
        blank=True,
    )
    acquired_by = M2M(to=Profile, related_name='biography_packets', blank=True)
    
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
