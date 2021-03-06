import os
import re

from PIL import Image
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.db.models import (
    BooleanField,
    CASCADE,
    Case,
    CharField,
    ImageField,
    IntegerField,
    Manager,
    Model,
    OneToOneField,
    Prefetch,
    Value,
    When,
)


class ReplaceFileStorage(FileSystemStorage):

    def get_available_name(self, name, max_length=None):
        """
        Returns a filename that's free on the target storage system, and
        available for new content to be written to.
        Found at http://djangosnippets.org/snippets/976/
        This file storage solves overwrite on upload problem.
        """
        # If the filename already exists, remove it
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name

    def get_valid_name(self, name):
        """Overrides method which would normally replace whitespaces with
        underscores and remove special characters.
            s = str(s).strip().replace(' ', '_')
            return re.sub(r'(?u)[^-\w.]', '', s)
        Modified to leave whitespace and to accept it in regular expressions.
        """
        name = str(name).strip()
        return re.sub(r'(?u)[^-\w.\s]', '', name)
    
    
STATUS = [
    ('gm', 'MG'),
    ('npc', 'BN'),
    ('player', 'GRACZ'),
]


class NonGMProfileManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(status__in=['player', 'npc'])
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


class LivingProfileManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(status__in=['player', 'npc'])
        qs = qs.filter(is_alive=True)
        return qs


class ContactableProfileManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(status__in=['gm', 'player'])
        qs = qs.filter(is_active=True)
        return qs


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
        storage=ReplaceFileStorage(),
    )
    # Character name copied from Character (by signal) to avoid queries
    copied_character_name = CharField(max_length=100, blank=True, null=True)
    
    objects = Manager()
    non_gm = NonGMProfileManager()
    players = PlayerProfileManager()
    active_players = ActivePlayerProfileManager()
    npcs = NPCProfileManager()
    living = LivingProfileManager()
    contactables = ContactableProfileManager()

    class Meta:
        ordering = ['-status', '-is_active', 'user__username']
    
    def __str__(self):
        return self.copied_character_name or self.user.username

    def save(self, *args, **kwargs):
        first_save = True if not self.pk else False
        super().save(*args, **kwargs)
        if first_save and self.image:
            img = Image.open(self.image.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.image.path)

    @staticmethod
    def _characters_all_related(qs):
        qs = qs.prefetch_related('known_directly', 'known_indirectly')
        qs = qs.select_related('profile')
        return qs

    def characters_all_known(self):
        if self.status == 'gm':
            from prosoponomikon.models import Character
            qs = Character.objects.all()
        else:
            known_dir = self.characters_known_directly.all()
            known_indir = self.characters_known_indirectly.all()
            qs = (known_dir | known_indir).distinct()
        return self._characters_all_related(qs).exclude(id=self.character.id)
    
    def characters_known_only_indirectly(self):
        if self.status == 'gm':
            from prosoponomikon.models import Character
            qs = Character.objects.none()
        else:
            known_dir = self.characters_known_directly.all()
            known_indir = self.characters_known_indirectly.all()
            qs = known_indir.exclude(id__in=known_dir)
        return self._characters_all_related(qs).exclude(id=self.character.id)

    def characters_all_known_annotated_if_indirectly(self):
        from prosoponomikon.models import Character
        if self.status == 'gm':
            qs = Character.objects.all()
        else:
            known_only_indir = self.characters_known_only_indirectly()
            all_known = self.characters_all_known()
            qs = all_known.annotate(
                only_indirectly=Case(
                    When(id__in=known_only_indir, then=Value(1)),
                    default=Value(0),
                    output_field=IntegerField(),
                ),
            )
        return self._characters_all_related(qs).exclude(id=self.character.id)

    def characters_groups_authored_with_characters(self):
        characters = self.characters_all_known_annotated_if_indirectly()
        character_groups = self.character_groups_authored.all()
        character_groups = character_groups.prefetch_related(
            Prefetch('characters', queryset=characters),
            'characters__profile__user',
            'characters__known_directly',
            'characters__known_indirectly',
            'characters__first_name')
        return character_groups
