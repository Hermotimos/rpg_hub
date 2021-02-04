import datetime

from PIL import Image
from django.db.models import (
    BooleanField,
    CharField,
    CASCADE,
    DateTimeField,
    ForeignKey as FK,
    ImageField,
    ManyToManyField as M2MField,
    Model,
    PROTECT,
    TextField,
)
from django.db.models.signals import post_save

from users.models import Profile


class Topic(Model):
    title = CharField(max_length=77, unique=True, verbose_name='Temat narady')
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


class Debate(Model):
    name = CharField(max_length=77, unique=True, verbose_name='Tytuł narady')
    topic = FK(to=Topic, related_name='debates', on_delete=CASCADE)
    known_directly = M2MField(
        to=Profile,
        related_name='debates_known_directly',
        verbose_name='Uczestnicy',
        help_text="""
            ***Aby zaznaczyć wiele postaci - użyj CTRL albo SHIFT.<br><br>
            1) Włączaj tylko postacie znajdujące się w pobliżu w chwili
                zakończenia ostatniej sesji.<br>
            2) Postacie w pobliżu niewłączone do narady mogą to zauważyć.<br>
            3) Jeśli chcesz zaczekać na sposobny moment, powiadom MG.<br>
            4) Jeśli na liście brakuje postaci, powiadom MG.<br><br>
        """
    )
    is_ended = BooleanField(default=False)
    is_individual = BooleanField(verbose_name='Narada indywidualna?')
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name
    
    def informables(self):
        qs = Profile.active_players.all()
        qs = qs.exclude(id__in=self.known_directly.all())
        return qs


class Remark(Model):
    text = TextField()
    debate = FK(to=Debate, related_name='remarks', on_delete=CASCADE)
    author = FK(
        to=Profile,
        related_name='remarks',
        on_delete=PROTECT,
        verbose_name='Autor',
    )
    image = ImageField(
        upload_to='post_pics',
        blank=True,
        null=True,
        verbose_name='Obraz',
    )
    seen_by = M2MField(to=Profile, related_name='remarks_seen', blank=True)
    created_at = DateTimeField(auto_now_add=True)

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
    start = instance.created_at - datetime.timedelta(minutes=1)
    end = instance.created_at
    doubled = Remark.objects.filter(
        debate=instance.debate,
        text=instance.text,
        author=instance.author,
        created_at__range=[start, end],
    )
    if doubled.count() > 1:
        instance.delete()


post_save.connect(delete_if_doubled, sender=Remark)
