import datetime

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
from django.dispatch import receiver

from rpg_project.utils import ensure_unique_filename, clear_cache
from users.models import Profile


class Demand(Model):
    author = FK(to=Profile, related_name='authored_demands', on_delete=CASCADE)
    addressee = FK(
        to=Profile, related_name='received_demands', on_delete=CASCADE)
    text = TextField()
    date_created = DateTimeField(auto_now_add=True)
    image = ImageField(upload_to='contact_pics', blank=True, null=True)
    is_done = BooleanField(default=False)

    class Meta:
        ordering = ['-date_created']

    def __str__(self):
        text = self.text
        return f'{text[0:50] + "..." if len(str(text)) > 50 else text}'

    def save(self, *args, **kwargs):
        if self.image:
            self.image.name = ensure_unique_filename(self.image.name)
        super().save(*args, **kwargs)


class DemandAnswer(Model):
    demand = FK(to=Demand, related_name='demand_answers', on_delete=CASCADE)
    author = FK(to=Profile, related_name='demand_answers', on_delete=CASCADE)
    text = TextField()
    date_posted = DateTimeField(auto_now_add=True)
    image = ImageField(upload_to='contact_pics', blank=True, null=True)

    class Meta:
        ordering = ['date_posted']

    def __str__(self):
        text = self.text
        return f'{text[0:100] + "..." if len(str(text)) > 100 else text}'

    def save(self, *args, **kwargs):
        if self.image:
            self.image.name = ensure_unique_filename(self.image.name)
        super().save(*args, **kwargs)


class Plan(Model):
    author = FK(to=Profile, related_name='plans', on_delete=CASCADE)
    text = TextField()
    inform_gm = BooleanField(default=False)
    date_created = DateTimeField(auto_now_add=True)
    image = ImageField(upload_to='contact_pics', blank=True, null=True)

    class Meta:
        ordering = ['-date_created']

    def __str__(self):
        text = self.text
        return f'{text[0:100] + "..." if len(str(text)) > 100 else text}'

    def save(self, *args, **kwargs):
        if self.image:
            self.image.name = ensure_unique_filename(self.image.name)
        super().save(*args, **kwargs)


# ---------------------------------------

# Signals


@receiver(post_save, sender=DemandAnswer)
def delete_if_doubled(sender, instance, **kwargs):
    time_span = datetime.datetime.now() - datetime.timedelta(minutes=2)
    doubled = DemandAnswer.objects.filter(
        text=instance.text,
        author=instance.author,
        date_posted__gte=time_span,
    )
    if doubled.count() > 1:
        instance.delete()


@receiver(post_save, sender=Demand)
def remove_cache(sender, instance, **kwargs):
    """
    Remove navbar cache on Demand save (creation or 'is_done' change)
    for all participants.
    """
    vary_on_list = [[instance.author.user.id, instance.addressee.user.id]]
    clear_cache(cachename='navbar', vary_on_list=vary_on_list)
