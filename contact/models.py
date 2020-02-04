import datetime
from django.db import models
from django.db.models.signals import post_save
from users.models import User
from PIL import Image


class Demand(models.Model):
    author = models.ForeignKey(User, related_name='authored_demands', on_delete=models.CASCADE)
    addressee = models.ForeignKey(User, related_name='received_demands', on_delete=models.CASCADE)
    text = models.TextField(max_length=4000)
    date_created = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='contact_pics', blank=True, null=True)
    is_done = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date_created']

    def __str__(self):
        return f'{self.text[0:50]}...' if len(str(self.text)) > 50 else self.text

    def save(self, *args, **kwargs):
        first_save = True if not self.pk else False
        super().save(*args, **kwargs)
        if first_save and self.image:
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
        ordering = ['date_posted']

    def save(self, *args, **kwargs):
        first_save = True if not self.pk else False
        super().save(*args, **kwargs)
        if first_save and self.image:
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
    image = models.ImageField(upload_to='contact_pics', blank=True, null=True)

    def __str__(self):
        return f'{self.text[0:100] if len(str(self.text)) > 100 else self.text}...'

    def save(self, *args, **kwargs):
        first_save = True if not self.pk else False
        super().save(*args, **kwargs)
        if first_save and self.image:
            img = Image.open(self.image.path)
            if img.height > 700 or img.width > 700:
                output_size = (700, 700)
                img.thumbnail(output_size)
                img.save(self.image.path)

    class Meta:
        ordering = ['-date_created']


# ---------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------- SIGNALS ---------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------


def delete_if_doubled(sender, instance, **kwargs):
    time_span = datetime.datetime.now() - datetime.timedelta(minutes=2)
    doubled = DemandAnswer.objects.filter(text=instance.text, author=instance.author, date_posted__gte=time_span)
    if doubled.count() > 1:
        instance.delete()


post_save.connect(delete_if_doubled, sender=DemandAnswer)

