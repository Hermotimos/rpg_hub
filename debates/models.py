from django.db import models
from django.contrib.auth.models import User
from django.db.models import Max, Min
from PIL import Image
from users.models import Profile


class Topic(models.Model):
    title = models.CharField(max_length=50, unique=True, verbose_name='tytuł tematu')
    date_created = models.DateTimeField(auto_now_add=True)
    # date_updated = models.DateTimeField(auto_now=True)
    description = models.CharField(max_length=100, verbose_name='opis tematu', blank=True, null=True)

    class Meta:
        ordering = ['-date_created']

    def __str__(self):
        return self.title

    def allowed_list(self):
        allowed_profiles = []
        for debate in self.debates.all():
            for profile in debate.allowed_profiles.all():
                allowed_profiles.append(profile)
        return allowed_profiles


class Debate(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='tytuł narady')
    date_created = models.DateTimeField(auto_now_add=True)
    # date_updated = models.DateTimeField(auto_now=True)
    topic = models.ForeignKey(Topic, related_name='debates', on_delete=models.CASCADE)
    starter = models.ForeignKey(User, related_name='debates', on_delete=models.CASCADE)
    allowed_profiles = models.ManyToManyField(to=Profile, related_name='allowed_debates')
    is_ended = models.BooleanField(default=False)
    is_individual = models.BooleanField(default=False)
    followers = models.ManyToManyField(to=Profile, related_name='followed_debates', blank=True)

    class Meta:
        ordering = ['-date_created']

    def __str__(self):
        return self.name

    def first_player_remark_date(self):
        players_remarks = self.remarks.exclude(
            author__profile__in=Profile.objects.filter(character_status='gm'))
        return players_remarks.aggregate(Min('date_posted'))['date_posted__min']

    def last_player_remark_date(self):
        players_remarks = self.remarks.exclude(
            author__profile__in=Profile.objects.filter(character_status='gm'))
        return players_remarks.aggregate(Max('date_posted'))['date_posted__max']

    def first_active_player(self):
        remark = self.remarks.get(date_posted=self.first_player_remark_date())
        return remark.author.profile.character_name if remark else ''

    def last_active_player(self):
        remark = self.remarks.get(date_posted=self.last_player_remark_date())
        return remark.author.profile.character_name if remark else ''

    def player_remarks_count(self):
        players_remarks = self.remarks.exclude(
            author__profile__in=Profile.objects.filter(character_status='gm'))
        return players_remarks.count()


class Remark(models.Model):
    text = models.TextField(max_length=4000)
    debate = models.ForeignKey(Debate, related_name='remarks', on_delete=models.CASCADE)
    date_posted = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, related_name='remarks', on_delete=models.CASCADE)
    image = models.ImageField(blank=True, null=True, upload_to='post_pics')

    def __str__(self):
        return f'{self.text[:50]}...'

    def text_begin(self):
        return self.__str__()

    def save(self, *args, **kwargs):
        super().save()
        if self.image:
            img = Image.open(self.image.path)
            if img.height > 700 or img.width > 700:
                output_size = (700, 700)
                img.thumbnail(output_size)
                img.save(self.image.path)
