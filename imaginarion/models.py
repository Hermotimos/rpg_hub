from PIL import Image
from django.db.models import (
    BooleanField,
    CASCADE,
    CharField,
    ForeignKey as FK,
    ImageField,
    Manager,
    ManyToManyField as M2M,
    Model,
    PROTECT,
    TextField,
)

from rpg_project.utils import ReplaceFileStorage, create_sorting_name

# TODO rename app 'imaginarion' -> 'mousarion'

AUDIO_TYPES = (
    ('domeny', 'DOMENY'),
    ('npc', 'NPC'),
    ('topoi', 'TOPOI'),
    ('varia', 'VARIA'),
)


class Audio(Model):
    """A model to store paths to externally stored audio files."""
    LINK_BLUEPRINT = 'https://docs.google.com/uc?export=download&id=[ID HERE]'
    
    # This doesn't work on PythonAnywhere... do they really handle Django 3.1?
    # class AudioType(models.TextChoices):
    #     domeny = 'DOMENY'
    #     npc = 'NPC'
    #     topoi = 'TOPOI'
    #     varia = 'VARIA'
    # type = models.CharField(max_length=5, choices=AudioType.choices)
    
    title = CharField(max_length=200)
    description = TextField(max_length=500, blank=True, null=True)
    type = CharField(max_length=10, choices=AUDIO_TYPES)
    path = TextField(default=LINK_BLUEPRINT)
    
    # For Google Drive construct path by:
    # https://docs.google.com/uc?export=download&id=XXXXXXXX
    # where XXXXXXXX equals file id take from the share link:
    # https://drive.google.com/file/d/XXXXXXXX/view?usp=sharing ==> XXXXXXXX
    # RESULT: https://docs.google.com/uc?export=download&id=XXXXXXXX
    
    class Meta:
        ordering = ['type', 'title']

    def __str__(self):
        return self.title

        
class AudioSet(Model):
    title = CharField(max_length=200)
    description = TextField(max_length=500, blank=True, null=True)
    main_audio = FK(to=Audio, on_delete=PROTECT)
    audios = M2M(to=Audio, related_name='audio_sets', blank=True)
    
    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


# TODO osobno w każdej app odpalać pętlę, która:
#   1) zaktualizuje 'type'
#   2) zapisze obraz w nowej lokacji (storage.blob)
#   3) zaktualizuje ścieżkę w ImagePicture - to chyba nie takie proste
# TODO zapis bez jakichkolwiek prefiksów
# TODO symbola -> realia_symbola
# TODO add 'type'
class PictureImage(Model):
    TYPES = (
        ('toponomikon-main', 'toponomikon-main'),
        ('toponomikon-other', 'toponomikon-other'),
        ('prosoponomikon-main', 'prosoponomikon-main'),
        ('prosoponomikon-other', 'prosoponomikon-other'),
        ('therionomikon', 'therionomikon'),
        ('knowledge', 'knowledge'),
        ('realia', 'realia'),
        ('varia', 'varia'),
    )
    """A model to store paths to internally stored image files."""
    image = ImageField(upload_to='post_pics', storage=ReplaceFileStorage())
    # type = CharField(max_length=20, choices=TYPES)
    description = CharField(max_length=200, blank=True, null=True)
    sorting_name = CharField(max_length=250, blank=True, null=True)

    class Meta:
        ordering = ['sorting_name']
        
    def save(self, *args, **kwargs):
        # TODO add re-save of image (to enforce new location on type change)
        self.sorting_name = create_sorting_name(self.__str__())
        first_save = True if not self.pk else False
        super().save(*args, **kwargs)
        if first_save and self.image:
            img = Image.open(self.image.path)
            if img.height > 1000 or img.width > 1000:
                output_size = (1000, 1000)
                img.thumbnail(output_size)
                img.save(self.image.path)

    def __str__(self):
        return str(self.image.name).replace("post_pics/", "")


IMG_TYPES = (
    ('knowledge', 'KNOWLEDGE'),
    ('npc', 'NPC'),
    ('players-notes', 'PLAYERS-NOTES'),
    ('profile', 'PROFILE'),
    ('realia', 'REALIA'),
    ('symbola', 'SYMBOLA'),
    ('thera', 'THERA'),
    ('topoi', 'TOPOI'),
    ('varia', 'VARIA'),
)


class Picture(Model):
    """An overlay model to create contextual descriptions for Image objects.
    One Image object may have multiple descriptions depending on the context
    in which it was seen and to whom it is known. This allows to create
    multiple overlays for one image with varying descriptions and types.
    """
    image = FK(to=PictureImage, related_name='pictures', on_delete=CASCADE)
    type = CharField(max_length=20, choices=IMG_TYPES)
    description = CharField(max_length=200, blank=True, null=True)
    sorting_name = CharField(max_length=250, blank=True, null=True)

    class Meta:
        ordering = ['type', 'sorting_name']

    def __str__(self):
        return f"[{self.type.upper()}] {self.description}"

    def save(self, *args, **kwargs):
        self.sorting_name = create_sorting_name(self.description)
        super().save(*args, **kwargs)


class PictureSetManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.prefetch_related('pictures__image')
        return qs


class PictureSet(Model):
    objects = PictureSetManager()
    
    title = CharField(max_length=200)
    pictures = M2M(to=Picture, related_name='picture_sets', blank=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title
