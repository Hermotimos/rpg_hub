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
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver

# from associations.models import Comment
from imaginarion.models import PictureSet
from rules.models import Skill
from users.models import Profile
from rpg_project.utils import OrderByPolish, clear_cache, profiles_to_userids


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


# ---------------------------------------

# Signals


@receiver(post_save, sender=KnowledgePacket)
@receiver(m2m_changed, sender=KnowledgePacket.skills.through)
@receiver(m2m_changed, sender=KnowledgePacket.references.through)
@receiver(m2m_changed, sender=KnowledgePacket.picture_sets.through)
def remove_cache(sender, instance, **kwargs):
    """
    Clear almanac cache on KnowledgePacket save or when there's a change in any
    of its M2M fields' list.
    """
    userids = profiles_to_userids(
        instance.acquired_by.all() | Profile.objects.filter(status='gm')
    )
    vary_on_list = [[userid] for userid in userids]

    clear_cache(cachename='almanac', vary_on_list=vary_on_list)


@receiver(post_save, sender=Skill)
@receiver(post_save, sender=Reference)
@receiver(post_save, sender=PictureSet)
def remove_cache(sender, instance, **kwargs):
    """
    Clear almanac cache whenever a Skill, a Reference or a PictureSet related
    to a KnowledgePacket is saved.
    """
    profiles = Profile.objects.filter(status='gm')
    for knowledge_packet in instance.knowledge_packets.all():
        profiles |= knowledge_packet.acquired_by.all()
    userids = profiles_to_userids(profiles)
    print(userids)
    vary_on_list = [[userid] for userid in userids]

    clear_cache(cachename='almanac', vary_on_list=vary_on_list)
