from django.db import models
from PIL import Image
from rpg_project.utils import ReplaceFileStorage


# TODO rename app 'imaginarion' -> 'mousarion'


class Audio(models.Model):
    """A model to store paths to externally stored audio files."""
    
    class AudioType(models.TextChoices):
        npc = 'NPC'
        topoi = 'TOPOI'
        varia = 'VARIA'
    
    type = models.CharField(max_length=5, choices=AudioType.choices)
    path = models.TextField()
    title = models.CharField(max_length=200, blank=True, null=True)
    info = models.TextField(max_length=500, unique=True, blank=True, null=True)
    
    class Meta:
        ordering = ['type', 'title']

    def __str__(self):
        return f'{str(self.type)}: {self.title}'


# TODO delete model, below is a replacement model (work with existing objs...)
TYPES = (
    ('knowledge', 'KNOWLEDGE'),
    ('npc', 'NPC'),
    ('realia', 'REALIA'),
    ('symbola', 'SYMBOLA'),
    ('thera', 'THERA'),
    ('topoi', 'TOPOI'),
    ('varia', 'VARIA'),
)


class Picture(models.Model):
    """A model to store paths to internally stored image files."""

    image = models.ImageField(upload_to='post_pics',
                              storage=ReplaceFileStorage())
    type = models.CharField(max_length=10, choices=TYPES)
    title = models.CharField(max_length=200, unique=True)
    description = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        ordering = ['type', 'title', 'description']

    def __str__(self):
        return f'{str(self.type).upper()}_{str(self.title).split("_", 1)[1]}'

    def save(self, *args, **kwargs):
        first_save = True if not self.pk else False
        super().save(*args, **kwargs)
        if first_save and self.image:
            img = Image.open(self.image.path)
            if img.height > 1000 or img.width > 1000:
                output_size = (1000, 1000)
                img.thumbnail(output_size)
                img.save(self.image.path)
                
                
# TODO: REPLACEMENT !!!!
# class Picture(models.Model):
#
#     class PictureType(models.TextChoices):
#         knowledge = 'KNOW'
#         npc = 'NPC'
#         realia = 'REAL'
#         symbola = 'SYMB'
#         thera = 'THERA'
#         topoi = 'TOPOI'
#         varia = 'VARIA'
#
#     type = models.CharField(max_length=5, choices=PictureType.choices)
#     image = models.ImageField(upload_to='post_pics',
#                               storage=ReplaceFileStorage())
#     title = models.CharField(max_length=200, unique=True)
#     description = models.CharField(max_length=200, blank=True, null=True)
#
#     class Meta:
#         ordering = ['type', 'title', 'description']
#
#     def __str__(self):
#         return f'{str(self.type).upper()}__{str(self.title).split("_", 1)[1]}'
#
#     def save(self, *args, **kwargs):
#         first_save = True if not self.pk else False
#         super().save(*args, **kwargs)
#         if first_save and self.image:
#             img = Image.open(self.image.path)
#             if img.height > 1000 or img.width > 1000:
#                 output_size = (1000, 1000)
#                 img.thumbnail(output_size)
#                 img.save(self.image.path)


