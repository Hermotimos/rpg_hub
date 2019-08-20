from django.db import models
from PIL import Image


TYPES = (
    ('npc', 'NPC'),
    ('realia', 'REALIA'),
    ('symbola', 'SYMBOLA'),
    ('thera', 'THERA'),
    ('topoi', 'TOPOI'),
    ('varia', 'VARIA'),
)


class Picture(models.Model):
    image = models.ImageField(upload_to='post_pics')
    type = models.CharField(max_length=10, choices=TYPES)
    title = models.CharField(max_length=200, unique=True)
    description = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        ordering = ['type', 'description']

    def __str__(self):
        return f'{str(self.type).upper()}___{str(self.title).split("_", 1)[1]}'

    def admin_title(self):
        return self.__str__()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.image:
            img = Image.open(self.image.path)
            if img.height > 1000 or img.width > 1000:
                output_size = (1000, 1000)
                img.thumbnail(output_size)
                img.save(self.image.path)
