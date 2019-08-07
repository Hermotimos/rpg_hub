from django.db import models
from PIL import Image


TYPES = (
    ('person', 'person'),
    ('place', 'place'),
    ('thing', 'thing'),
    ('knowledge', 'knowledge')
)


class Picture(models.Model):
    title = models.CharField(max_length=200, unique=True)
    description = models.CharField(max_length=200)
    type = models.CharField(max_length=10, choices=TYPES)
    image = models.ImageField(blank=True, null=True, upload_to='post_pics')

    class Meta:
        ordering = ['type']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.image:
            img = Image.open(self.image.path)
            if img.height > 1000 or img.width > 1000:
                output_size = (1000, 1000)
                img.thumbnail(output_size)
                img.save(self.image.path)
