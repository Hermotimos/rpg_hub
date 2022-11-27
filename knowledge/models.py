from django.contrib.contenttypes.fields import GenericRelation
from django.db.models import (
    CharField,
    ForeignKey as FK,
    ManyToManyField as M2M,
    Model,
    SmallIntegerField,
    PROTECT,
    TextField,
    URLField,
)

# from associations.models import Comment
from imaginarion.models import PictureSet
from rules.models import Skill
from users.models import Profile
from rpg_project.utils import OrderByPolish


# -----------------------------------------------------------------------------


class Reference(Model):
    title = CharField(max_length=100, unique=True)
    description = TextField()
    url = URLField(max_length=500)
    
    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


# -----------------------------------------------------------------------------


class InfoPacket(Model):
    title = CharField(max_length=100, unique=True)
    text = TextField(blank=True, null=True)
    # comments = GenericRelation(Comment)

    class Meta:
        abstract = True
        ordering = [OrderByPolish('title')]
        
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
    picture_sets = M2M(to=PictureSet, related_name='biography_packets', blank=True)
    order_no = SmallIntegerField(default=1)

    class Meta:
        ordering = ['order_no', OrderByPolish('title')]
   

class KnowledgePacket(InfoPacket):
    """A class for info packets that might be shared among multiple Skills."""
    author = FK(
        to=Profile,
        related_name='authored_kn_packets',
        on_delete=PROTECT,
        null=True,
        blank=True)
    acquired_by = M2M(to=Profile, related_name='knowledge_packets', blank=True)
    skills = M2M(to=Skill, related_name='knowledge_packets')
    picture_sets = M2M(to=PictureSet, related_name='knowledge_packets', blank=True)
    references = M2M(to=Reference, related_name='knowledge_packets', blank=True)
    
    
class MapPacket(InfoPacket):
    acquired_by = M2M(to=Profile, related_name='map_packets', blank=True)
    picture_sets = M2M(to=PictureSet, related_name='map_packets')
