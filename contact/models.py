from django.db import models
from users.models import User
from PIL import Image


class Demand(models.Model):
    author = models.ForeignKey(User, related_name='authored_demands', on_delete=models.CASCADE)
    addressee = models.ForeignKey(User, related_name='received_demands', on_delete=models.CASCADE)
    text = models.TextField(max_length=4000)
    date_created = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(blank=True, null=True, upload_to='contact_pics')
    is_done = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date_created']

    def __str__(self):
        return f'{self.text[0:50]}...'

    def save(self, *args, **kwargs):
        super().save()
        if self.image:
            img = Image.open(self.image.path)
            if img.height > 700 or img.width > 700:
                output_size = (700, 700)
                img.thumbnail(output_size)
                img.save(self.image.path)


class DemandAnswer(models.Model):
    demand = models.ForeignKey(Demand, related_name='demand_answers', on_delete=models.CASCADE)
    author = models.ForeignKey(User, related_name='demand_answers', on_delete=models.CASCADE)
    text = models.TextField(max_length=4000)
    date_posted = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(blank=True, null=True, upload_to='contact_pics')

    class Meta:
        ordering = ['-date_posted']

    def save(self, *args, **kwargs):
        super().save()
        if self.image:
            img = Image.open(self.image.path)
            if img.height > 700 or img.width > 700:
                output_size = (700, 700)
                img.thumbnail(output_size)
                img.save(self.image.path)

    def __str__(self):
        return f'{self.text[0:100] if len(str(self.text)) > 100 else self.text}...'


class Plan(models.Model):
    author = models.ForeignKey(User, related_name='plans', on_delete=models.CASCADE)
    inform_gm = models.BooleanField(default=False)
    text = models.TextField(max_length=4000)
    date_created = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(blank=True, null=True, upload_to='contact_pics')

    def __str__(self):
        return f'{self.text[0:100] if len(str(self.text)) > 100 else self.text}...'

    def save(self, *args, **kwargs):
        super().save()
        if self.image:
            img = Image.open(self.image.path)
            if img.height > 700 or img.width > 700:
                output_size = (700, 700)
                img.thumbnail(output_size)
                img.save(self.image.path)

    class Meta:
        ordering = ['-date_created']
