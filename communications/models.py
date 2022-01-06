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

from users.models import Profile


class Topic(Model):
    title = CharField(max_length=100, unique=True)
    order_no = SmallIntegerField(default=100)
    created_at = DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order_no', 'title']
    
    def __str__(self):
        return self.title


#  ==========================================================================


THREAD_KINDS = (
    ('Announcement', 'Announcement'),   # User
    ('Debate', 'Debate'),               # Profile
    ('Demand', 'Demand'),               # Profile
    # ('Plan', 'Plan'),                   # Profile
    # ('Report', 'Report'),               # User
)


class ThreadTag(Model):
    title = CharField(max_length=20)
    author = FK(to=Profile, related_name='thread_tags', on_delete=CASCADE)
    color = CharField(max_length=7, default='#000000')
    kind = CharField(max_length=15, choices=THREAD_KINDS)

    class Meta:
        ordering = ['kind', 'author', 'title']
        unique_together = ['title', 'author', 'kind']

    def __str__(self):
        return f"#{self.title}"


class Thread(Model):
    title = CharField(max_length=100, unique=True)
    topic = FK(to=Topic, related_name='threads', on_delete=CASCADE)             # TODO maybe blank=True, null=True for demands, plans
    kind = CharField(max_length=15, choices=THREAD_KINDS)
    known_directly = M2M(to=Profile, related_name='threads_known_directly')     # known_directly also use instead of inform_gm in Plans
    created_at = DateTimeField(auto_now_add=True)
    # Announcement
    followers = M2M(to=Profile, related_name='threads_followed', blank=True)
    tags = M2M(to=ThreadTag, related_name='threads', blank=True)
    # Debate
    is_ended = BooleanField(default=False)                                      # also Demands instead of is_done
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
        return f'/communications/thread:{self.pk}/None/#page-bottom'


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


#  ==========================================================================


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
    
    
#  ==========================================================================


class Statement(Model):
    text = TextField()
    thread = FK(to=Thread, related_name='statements', on_delete=CASCADE)
    author = FK(to=Profile, related_name='statements', on_delete=PROTECT)
    image = ImageField(upload_to='post_pics', blank=True, null=True)
    seen_by = M2M(to=Profile, related_name='statements_seen', blank=True)
    created_at = DateTimeField(auto_now_add=True)
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


def delete_if_doubled(sender, instance, **kwargs):
    start = instance.created_at - datetime.timedelta(minutes=2)
    end = instance.created_at
    identical = Statement.objects.filter(
        thread=instance.thread,
        text__iexact=instance.text,
        author=instance.author,
        created_at__range=[start, end],
    )
    if identical.count() > 1:
        instance.delete()


post_save.connect(delete_if_doubled, sender=Statement)
