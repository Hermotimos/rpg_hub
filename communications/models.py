import datetime

from PIL import Image
from django.db.models import (
    BooleanField,
    CharField,
    CASCADE,
    DateTimeField,
    ForeignKey as FK,
    ImageField,
    ManyToManyField as M2M,
    Model,
    PROTECT,
    SmallIntegerField,
    TextField,
)
from django.db.models.signals import post_save

from users.models import Profile


class Topic(Model):
    title = CharField(max_length=100, unique=True)
    order_no = SmallIntegerField(default=100)
    created_at = DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['title']
    
    def __str__(self):
        return self.title


class Thread(Model):
    THREAD_KINDS = (
        ('Debate', 'Debate'),
        ('Demand', 'Demand'),
        ('Discussion', 'Discussion'),
    )
    
    title = CharField(max_length=100, unique=True)
    topic = FK(to=Topic, related_name='threads', on_delete=CASCADE)
    kind = CharField(max_length=10, choices=THREAD_KINDS
                     # , blank=True, null=True
                     )
    known_directly = M2M(
        to=Profile,
        related_name='threads_known_directly')
    created_at = DateTimeField(auto_now_add=True)

    # Discussion
    followers = M2M(to=Profile, related_name='threads_followed', blank=True)
    # Debate
    is_ended = BooleanField(default=False)
    is_exclusive = BooleanField()
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return self.title
    
    def informables(self):
        # TODO separate informables function for each thread kind
        qs = Profile.living.all()
        qs = qs.exclude(id__in=self.known_directly.all())
        return qs


class Statement(Model):
    text = TextField()
    thread = FK(to=Thread, related_name='statements', on_delete=CASCADE)
    author = FK(to=Profile, related_name='statements', on_delete=PROTECT)
    image = ImageField(upload_to='post_pics', blank=True, null=True)
    seen_by = M2M(to=Profile, related_name='statements_seen', blank=True)
    created_at = DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']

    def __str__(self):
        text = self.text
        return f'{text[:100]}...' if len(str(text)) > 100 else text
    
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
# ---------------------------------------- SIGNALS ----------------------------
# -----------------------------------------------------------------------------


def delete_if_doubled(sender, instance, **kwargs):
    start = instance.created_at - datetime.timedelta(minutes=2)
    end = instance.created_at
    identical = Statement.objects.filter(
        thread=instance.thread,
        text=instance.text,
        author=instance.author,
        created_at__range=[start, end],
    )
    if identical.count() > 1:
        instance.delete()


post_save.connect(delete_if_doubled, sender=Statement)
