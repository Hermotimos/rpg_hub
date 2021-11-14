import datetime

from PIL import Image
from django.db.models import (
    BooleanField,
    CharField,
    CASCADE,
    DateTimeField,
    F,
    ForeignKey as FK,
    ImageField,
    Manager,
    ManyToManyField as M2M,
    Max,
    Model,
    PROTECT,
    SmallIntegerField,
    TextField,
)
from django.db.models.signals import post_save
from django.utils.safestring import mark_safe
from users.models import Profile
from rpg_project.utils import COLORS_CHOICES


class Topic(Model):
    title = CharField(max_length=100, unique=True)
    order_no = SmallIntegerField(default=100)
    created_at = DateTimeField(
        null=True,
        # auto_now_add=True TODO restore after data migration
    )
    
    class Meta:
        ordering = ['order_no', 'title']
    
    def __str__(self):
        return self.title


class ThreadTag(Model):
    title = CharField(max_length=30)
    author = FK(to=Profile, related_name='thread_tags', on_delete=CASCADE)
    color = CharField(max_length=7, choices=COLORS_CHOICES, default="#FF0000")

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title

    def _color(self):
        return mark_safe(
            f'<span style="color: {self.color};">{self.color}</span>')

    _color.admin_order_field = 'color'


class Thread(Model):
    THREAD_KINDS = (
        ('Debate', 'Debate'),
        ('Demand', 'Demand'),
        ('Announcement', 'Announcement'),
    )
    
    title = CharField(max_length=100, unique=True)
    topic = FK(to=Topic, related_name='threads', on_delete=CASCADE)
    kind = CharField(max_length=15, choices=THREAD_KINDS)
    known_directly = M2M(to=Profile, related_name='threads_known_directly')
    created_at = DateTimeField(
        null=True,
        # auto_now_add=True TODO restore after data migration
    )
    # Announcement
    followers = M2M(to=Profile, related_name='threads_followed', blank=True)
    tags = M2M(to=ThreadTag, related_name='threads', blank=True)
    # Debate
    is_ended = BooleanField(default=False)
    is_exclusive = BooleanField(default=False)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return self.title
    
    def informables(self):
        if self.kind == 'Announcement':
            qs = Profile.active_players.all()
        elif self.kind == 'Debate':
            qs = Profile.living.all()
        else:
            qs = Profile.objects.none()
        return qs.exclude(id__in=self.known_directly.all())

    def get_absolute_url(self):
        return f'/communications/thread:{self.pk}'


class DebateManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(kind='Debate')
        return qs


class Debate(Thread):
    objects = DebateManager()
    
    class Meta:
        proxy = True


class AnnouncementManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(kind='Announcement')
        qs = qs.annotate(last_activity=Max(F('statements__created_at')))
        return qs


class Announcement(Thread):
    objects = AnnouncementManager()
    
    class Meta:
        proxy = True


class Option(Model):
    author = FK(to=Profile, related_name='options', on_delete=CASCADE)
    text = CharField(max_length=50)
    voters_yes = M2M(to=Profile, related_name='options_votes_yes', blank=True)
    voters_no = M2M(to=Profile, related_name='options_votes_no', blank=True)
    
    class Meta:
        ordering = ['text']
    
    def __str__(self):
        text = self.text
        return f'{text[:100]}...' if len(str(text)) > 100 else text
    
    
class Statement(Model):
    text = TextField()
    thread = FK(to=Thread, related_name='statements', on_delete=CASCADE)
    author = FK(to=Profile, related_name='statements', on_delete=PROTECT)
    image = ImageField(upload_to='post_pics', blank=True, null=True)
    seen_by = M2M(to=Profile, related_name='statements_seen', blank=True)
    created_at = DateTimeField(
        null=True,
        # auto_now_add=True TODO restore after data migration
    )
    # Announcement
    options = M2M(to=Option, related_name='threads', blank=True)

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

# TODO restore when create_at is auto field again
# def delete_if_doubled(sender, instance, **kwargs):
#     start = instance.created_at - datetime.timedelta(minutes=2)
#     end = instance.created_at
#     identical = Statement.objects.filter(
#         thread=instance.thread,
#         text=instance.text,
#         author=instance.author,
#         created_at__range=[start, end],
#     )
#     if identical.count() > 1:
#         instance.delete()
#
#
# post_save.connect(delete_if_doubled, sender=Statement)
