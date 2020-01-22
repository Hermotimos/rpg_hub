from django.db import models

from imaginarion.models import Picture
from rpg_project.utils import create_sorting_name
from users.models import Profile


class KnowledgePacketType(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class KnowledgePacket(models.Model):
    title = models.CharField(max_length=100, unique=True)
    packet_types = models.ManyToManyField(KnowledgePacketType, related_name='knowledge_packets')
    text = models.TextField()
    pictures = models.ManyToManyField(Picture, related_name='knowledge_packets', blank=True)
    allowed_profiles = models.ManyToManyField(Profile, related_name='allowed_knowledge_packets', blank=True)
    sorting_name = models.CharField(max_length=250, blank=True, null=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.sorting_name = create_sorting_name(self.__str__())
        super(KnowledgePacket, self).save(*args, **kwargs)

    class Meta:
        ordering = ['title']


# not working:
# def add_gms_to_allowed_profiles(sender, instance, **kwargs):
#     gms = Profile.objects.filter(character_status='gm')
#     for gm in gms:
#         if gm not in instance.allowed_profiles.all():
#             instance.allowed_profiles.add(gm)
#             instance.m2msave()
#
#
# post_save.connect(add_gms_to_allowed_profiles, sender=KnowledgePacket)
