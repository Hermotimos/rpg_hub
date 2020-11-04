from PIL import Image
from django.db.models import Model, CharField, TextField, ImageField, \
    ForeignKey, PROTECT, ManyToManyField

from rpg_project.utils import ReplaceFileStorage

# TODO rename app 'imaginarion' -> 'mousarion'

AUDIO_TYPES = (
    ('npc', 'NPC'),
    ('topoi', 'TOPOI'),
    ('varia', 'VARIA'),
)


class Audio(Model):
    """A model to store paths to externally stored audio files."""
    
    # This doesn't work on PythonAnywhere... do they really handle Django 3.1?
    # class AudioType(models.TextChoices):
    #     npc = 'NPC'
    #     topoi = 'TOPOI'
    #     varia = 'VARIA'
    # type = models.CharField(max_length=5, choices=AudioType.choices)
    
    title = CharField(max_length=200, blank=True, null=True)
    description = TextField(max_length=500, blank=True, null=True)
    type = CharField(max_length=5, choices=AUDIO_TYPES)
    path = TextField()
    
    class Meta:
        ordering = ['type', 'title']

    def __str__(self):
        return f'{str(self.type)}: {self.title}'


class AudioSet(Model):
    title = CharField(max_length=200)
    description = TextField(max_length=500, blank=True, null=True)
    main_audio = ForeignKey(
        to=Audio,
        on_delete=PROTECT,
    )
    audios = ManyToManyField(to=Audio, related_name='audio_sets', blank=True)
    
    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title

    
# TODO delete model, below is a replacement model (work with existing objs...)
IMG_TYPES = (
    ('knowledge', 'KNOWLEDGE'),
    ('npc', 'NPC'),
    ('realia', 'REALIA'),
    ('symbola', 'SYMBOLA'),
    ('thera', 'THERA'),
    ('topoi', 'TOPOI'),
    ('varia', 'VARIA'),
)


class Picture(Model):
    """A model to store paths to internally stored image files."""

    image = ImageField(upload_to='post_pics', storage=ReplaceFileStorage())
    type = CharField(max_length=10, choices=IMG_TYPES)
    title = CharField(max_length=200, unique=True)
    description = CharField(max_length=200, blank=True, null=True)

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


