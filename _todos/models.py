import datetime

from django.db import models


class TODOList(models.Model):
    MARKS = [
        (0, '0'),
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
    ]

    daydate = models.DateField(default=datetime.date.today, unique=True)

    # PSYCHE
    SUNWALK = models.BooleanField(default=False)
    MED = models.BooleanField(default=False)
    TETRIS = models.BooleanField(default=False)
    RELAX = models.BooleanField(default=False)

    # SOMA
    sleep = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    IForKETO = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    drinkfood = models.BooleanField(default=False)
    # --
    flaxseed = models.BooleanField(default=False)
    spirulina = models.BooleanField(default=False)
    lionsmane = models.BooleanField(default=False)
    pickles = models.BooleanField(default=False)
    fishoilord3 = models.BooleanField(default=False)
    water = models.BooleanField(default=False)
    # --
    coffeex2 = models.BooleanField(default=False)
    # noA = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    noA = models.PositiveSmallIntegerField(default=0)
    # --
    warmup = models.BooleanField(default=False)
    stretching = models.BooleanField(default=False)
    workout = models.TextField(blank=True, null=True)

    # NOOS
    CODE = models.BooleanField(default=False)
    ENG = models.BooleanField(default=False)
    DE = models.BooleanField(default=False)
    FR = models.BooleanField(default=False)
    UKR = models.BooleanField(default=False)

    # marks
    awareness = models.PositiveSmallIntegerField(choices=MARKS, null=True, blank=True)
    happiness = models.PositiveSmallIntegerField(choices=MARKS, null=True, blank=True)
    openness = models.PositiveSmallIntegerField(choices=MARKS, null=True, blank=True)
    focus = models.PositiveSmallIntegerField(choices=MARKS, null=True, blank=True)
    anger = models.PositiveSmallIntegerField(choices=MARKS, null=True, blank=True)
    fear = models.PositiveSmallIntegerField(choices=MARKS, null=True, blank=True)
    emptiness = models.PositiveSmallIntegerField(choices=MARKS, null=True, blank=True)
    chaos = models.PositiveSmallIntegerField(choices=MARKS, null=True, blank=True)

    # comments
    comments = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-daydate']

    @property
    def completion(self):
        # TODO
        pass


class Food(models.Model):
    name = models.CharField(max_length=100, unique=True)
    fat = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    protein = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    carbs = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    fiber = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    class Meta:
        ordering = ['name']


# class Serving(models.Model):
#     food = models.ForeignKey(to=Food, on_delete=models.PROTECT)
#     size = models.DecimalField(max_digits=5, decimal_places=2, default=0)

#     class Meta:
#         ordering = ['id']


# class DailyServings(models.Model):
#     daydate = models.DateField(default=datetime.date.today, unique=True)
#     servings = models.ManyToManyField(to=Serving)

#     class Meta:
#         ordering = ['-daydate']

# from django.contrib.contenttypes.models import ContentType
# content_type = ContentType.objects.filter(model=c_type)
# print(content_type)