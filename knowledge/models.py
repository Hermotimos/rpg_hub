from django.db.models import (
    CharField,
    ForeignKey as FK,
    ManyToManyField as M2M,
    Model,
    SmallIntegerField,
    PROTECT,
    TextField,
)

from imaginarion.models import PictureSet
from rules.models import Skill
from users.models import Profile


class InfoPacket(Model):
    title = CharField(max_length=100, unique=True)
    text = TextField(blank=True, null=True)

    class Meta:
        abstract = True
        ordering = ['title']
        
    def __str__(self):
        return self.title
        

class DialoguePacket(InfoPacket):
    """A class for per-Persona dialogue notes for Game Master."""
    pass


class BiographyPacket(InfoPacket):
    """A class for per-Persona info that may be visible to Players."""
    author = FK(
        to=Profile,
        related_name='authored_bio_packets',
        on_delete=PROTECT,
        null=True,
        blank=True)
    acquired_by = M2M(to=Profile, related_name='biography_packets', blank=True)
    picture_sets = M2M(
        to=PictureSet, related_name='biography_packets', blank=True)
    order_no = SmallIntegerField(default=1)

    class Meta:
        ordering = ['order_no', 'title']
   
    def informables(self):
        qs = Profile.active_players.all()
        qs = qs.exclude(id__in=self.acquired_by.all())
        qs = qs.exclude(id=self.author_id)
        qs = qs.select_related('character')
        return qs


class KnowledgePacket(InfoPacket):
    """A class for info packets that might be shared among multiple Skills."""
    author = FK(
        to=Profile,
        related_name='authored_kn_packets',
        on_delete=PROTECT,
        null=True,
        blank=True,
    )
    acquired_by = M2M(to=Profile, related_name='knowledge_packets', blank=True)
    skills = M2M(to=Skill, related_name='knowledge_packets')
    picture_sets = M2M(
        to=PictureSet, related_name='knowledge_packets', blank=True)
    
    def informables(self):
        qs = Profile.active_players.all()
        qs = qs.exclude(id__in=self.acquired_by.all())
        qs = qs.select_related('character')
        return qs
    

class MapPacket(InfoPacket):
    acquired_by = M2M(to=Profile, related_name='map_packets', blank=True)
    picture_sets = M2M(to=PictureSet, related_name='map_packets')
