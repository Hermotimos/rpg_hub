from django.db.models import (
    BooleanField,
    CASCADE,
    CharField,
    ImageField,
    Manager,
    Model,
    OneToOneField,
    Q,
)
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from PIL import Image


STATUS = [
    ('gm', 'MG'),
    ('npc', 'BN'),
    ('player', 'GRACZ'),

    # # players
    # ('active_player', 'Gracz'),
    # ('inactive_player', 'Nieaktywny gracz'),
    # ('dead_player', 'Martwy gracz'),
    # # npc
    # ('living_npc', 'BN'),
    # ('dead_npc', 'Martwy BN'),
]


class NonGMProfileManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.exclude(status='gm')


class ContactableProfileManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(status__in=['gm', 'player'])
        qs = qs.filter(is_active=True)
        return qs
    

class LivingProfileManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(is_alive=True)
        return qs
    

class DebatableProfileManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.exclude(status='gm')
        qs = qs.filter(is_alive=True)
        return qs
    

class PlayerProfileManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(status__icontains='player')


class ActivePlayerProfileManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(status__icontains='player', is_active=True)


class NPCProfileManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(status__icontains='npc')


class Profile(Model):
    user = OneToOneField(to=User, on_delete=CASCADE)
    status = CharField(max_length=50, choices=STATUS, default='npc')
    is_alive = BooleanField(default=True)
    is_active = BooleanField(default=True)
    image = ImageField(
        default='profile_pics/profile_default.jpg',
        upload_to='profile_pics',
        blank=True,
        null=True,
    )
    
    objects = Manager()
    contactables = ContactableProfileManager()
    debatables = DebatableProfileManager()
    non_gm = NonGMProfileManager()
    npcs = NPCProfileManager()
    players = PlayerProfileManager()
    active_players = ActivePlayerProfileManager()
    living = LivingProfileManager()
    
    class Meta:
        ordering = ['-status', '-is_active', 'user__username']
    
    def __str__(self):
        return self.persona.name or self.user.username
    
    def save(self, *args, **kwargs):
        first_save = True if not self.pk else False
        super().save(*args, **kwargs)
        if first_save and self.image:
            img = Image.open(self.image.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.image.path)


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        p = Profile.objects.create(user=instance)
        p.name = instance.username.replace('_', ' ')
        p.save()
