from django.db import models
from users.models import User, Profile
from PIL import Image


class Demand(models.Model):
    author = models.ForeignKey(Profile, related_name='authored_demands', on_delete=models.CASCADE)
    addressee = models.ForeignKey(Profile, related_name='received_demands', on_delete=models.CASCADE)
    text = models.TextField(max_length=4000)
    date_created = models.DateTimeField(auto_now_add=True)
    date_done = models.DateTimeField(blank=True, null=True)
    image = models.ImageField(blank=True, null=True, upload_to='contact_pics')
    is_done = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.text[0:50]}...'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.image:
            img = Image.open(self.image.path)
            if img.height > 700 or img.width > 700:
                output_size = (700, 700)
                img.thumbnail(output_size)
                img.save(self.image.path)

    class Meta:
        ordering = ['-date_done', '-date_created']


class DemandAnswer(models.Model):
    demand = models.ForeignKey(Demand, related_name='demand_answers', on_delete=models.CASCADE)
    author = models.ForeignKey(Profile, related_name='demand_answers', on_delete=models.CASCADE)
    text = models.TextField(max_length=4000)
    date_posted = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(blank=True, null=True, upload_to='contact_pics')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.image:
            img = Image.open(self.image.path)
            if img.height > 700 or img.width > 700:
                output_size = (700, 700)
                img.thumbnail(output_size)
                img.save(self.image.path)

