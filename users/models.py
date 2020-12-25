from django.db.models import (
    CASCADE,
    CharField,
    ImageField,
    Model,
    OneToOneField,
    Q,
)
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from PIL import Image


# TODO Statuses should be reworked. But they're used a lot in views and Q queries
STATUS = [
    # players
    ('active_player', 'Gracz'),
    ('inactive_player', 'Nieaktywny gracz'),
    ('dead_player', 'Martwy gracz'),
    # npc
    ('living_npc', 'BN'),
    ('dead_npc', 'Martwy BN'),
    # other
    ('gm', 'MG'),
]
PLAYERS = Q(status__in=[
    'active_player',
    'inactive_player',
    'dead_player',
])


class Profile(Model):
    user = OneToOneField(to=User, on_delete=CASCADE)
    status = CharField(max_length=50, choices=STATUS, default='living_npc')
    # TODO migrate character_name to character_name2 in Character
    character_name = CharField(max_length=50, default='')
    image = ImageField(
        default='profile_pics/profile_default.jpg',
        upload_to='profile_pics',
    )
    
    class Meta:
        ordering = ['status']
        # ordering = ['status', 'character_name']

    def __str__(self):
        return self.user.username
        # return f"{self.character_name or self.user.username}"
    
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
        p.character_name = instance.username.replace('_', ' ')
        p.save()
