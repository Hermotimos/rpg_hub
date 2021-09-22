from django.db.models import (
    CharField,
    ForeignKey as FK,
    ManyToManyField as M2M,
    Model,
    SmallIntegerField,
    PROTECT,
    TextField,
)

from imaginarion.models import Picture, PictureSet
from rpg_project.utils import create_sorting_name
from rules.models import Skill
from users.models import Profile


class InfoPacket(Model):
    title = CharField(max_length=100, unique=True, verbose_name='Tytuł')
    text = TextField(blank=True, null=True, verbose_name='Treść')
    sorting_name = CharField(max_length=250, blank=True, null=True)

    class Meta:
        abstract = True
        ordering = ['sorting_name']
        
    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.sorting_name = create_sorting_name(self.__str__())
        super().save(*args, **kwargs)
        

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
    pictures = M2M(to=Picture, related_name='biography_packets', blank=True)
    order_no = SmallIntegerField(default=1)

    class Meta:
        ordering = ['order_no', 'sorting_name']
   
    def informables(self):
        qs = Profile.active_players.all()
        qs = qs.exclude(id__in=self.acquired_by.all())
        qs = qs.exclude(id=self.author_id)
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
    pictures = M2M(
        to=Picture,
        related_name='knowledge_packets',
        blank=True,
        verbose_name='Obrazy',
    )
    skills = M2M(
        to=Skill,
        related_name='knowledge_packets',
        verbose_name='Umiejętności powiązane',
    )
    
    def informables(self):
        qs = Profile.active_players.all()
        qs = qs.exclude(id__in=self.acquired_by.all())
        return qs
    

class MapPacket(InfoPacket):
    acquired_by = M2M(to=Profile, related_name='map_packets', blank=True)
    picture_sets = M2M(to=PictureSet, related_name='map_packets')
