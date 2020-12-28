import datetime

from PIL import Image
from django.db.models import (
    BooleanField,
    CASCADE,
    DateTimeField,
    ForeignKey as FK,
    ImageField,
    Model,
    TextField,
)
from django.db.models.signals import post_save

from users.models import User


class Demand(Model):
    author = FK(to=User, related_name='authored_demands', on_delete=CASCADE)
    addressee = FK(
        to=User,
        related_name='received_demands',
        on_delete=CASCADE,
        verbose_name='Adresat',
    )
    text = TextField(verbose_name='Treść')
    date_created = DateTimeField(auto_now_add=True)
    image = ImageField(
        upload_to='contact_pics',
        blank=True,
        null=True,
        verbose_name='Obraz [opcjonalnie]',
    )
    is_done = BooleanField(default=False)

    class Meta:
        ordering = ['-date_created']

    def __str__(self):
        text = self.text
        return f'{text[0:50] + "..." if len(str(text)) > 50 else text}'

    def save(self, *args, **kwargs):
        first_save = True if not self.pk else False
        super().save(*args, **kwargs)
        
        if first_save and self.image:
            img = Image.open(self.image.path)
            if img.height > 700 or img.width > 700:
                output_size = (700, 700)
                img.thumbnail(output_size)
                img.save(self.image.path)


class DemandAnswer(Model):
    demand = FK(to=Demand, related_name='demand_answers', on_delete=CASCADE)
    author = FK(to=User, related_name='demand_answers', on_delete=CASCADE)
    text = TextField(verbose_name='Odpowiedź')
    date_posted = DateTimeField(auto_now_add=True)
    image = ImageField(
        upload_to='contact_pics',
        blank=True,
        null=True,
        verbose_name='Obraz [opcjonalnie]',
    )

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
        text = self.text
        return f'{text[0:100] + "..." if len(str(text)) > 100 else text}'


class Plan(Model):
    author = FK(to=User, related_name='plans', on_delete=CASCADE)
    text = TextField(verbose_name='Treść')
    inform_gm = BooleanField(default=False, verbose_name='Poinformuj MG')
    date_created = DateTimeField(auto_now_add=True)
    image = ImageField(
        upload_to='contact_pics',
        blank=True,
        null=True,
        verbose_name='Obraz [opcjonalnie]',
    )
    
    class Meta:
        ordering = ['-date_created']

    def __str__(self):
        text = self.text
        return f'{text[0:100] + "..." if len(str(text)) > 100 else text}'

    def save(self, *args, **kwargs):
        first_save = True if not self.pk else False
        super().save(*args, **kwargs)
        
        if first_save and self.image:
            img = Image.open(self.image.path)
            if img.height > 700 or img.width > 700:
                output_size = (700, 700)
                img.thumbnail(output_size)
                img.save(self.image.path)


# -----------------------------------------------------------------------------
# ----------------------------------- SIGNALS ---------------------------------
# -----------------------------------------------------------------------------


def delete_if_doubled(sender, instance, **kwargs):
    time_span = datetime.datetime.now() - datetime.timedelta(minutes=2)
    doubled = DemandAnswer.objects.filter(text=instance.text,
                                          author=instance.author,
                                          date_posted__gte=time_span)
    if doubled.count() > 1:
        instance.delete()


post_save.connect(delete_if_doubled, sender=DemandAnswer)

