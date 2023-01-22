import datetime

from django.db import models


# =============================================================================


def monthdate():
    y, m, _ = str(datetime.date.today()).split('-')
    return datetime.datetime.strptime(f"{y}-{m}-01", '%Y-%m-%d')


class Month(models.Model):
    monthdate = models.DateField(default=monthdate, unique=True)
    
    def __str__(self):
        return self.monthdate.strftime('%B %Y')
        
    class Meta:
        ordering = ['-monthdate']
        

# =============================================================================


def thismonth():
    obj, _ = Month.objects.get_or_create(monthdate=monthdate())
    return obj.id

        
class TODOList(models.Model):
    TODO_FIELDS = []
    INFO_FIELDS = []
    CONDITIONS = {}
    
    MARKS = [
        (0, '0'),
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
    ]

    month = models.ForeignKey(to=Month, on_delete=models.PROTECT, related_name="days", default=thismonth)
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

    
class TODOList2023Manager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(daydate__year="2023")
        return qs
    
    
class TODOList2023(TODOList):
    objects = TODOList2023Manager()

    INFO_FIELDS = [
        'comments',
        'awareness', 'happiness', 'openness', 'focus',
        'anger', 'fear', 'emptiness', 'chaos',
    ]
    TODO_FIELDS = [
        'SUNWALK', 'MED', 'TETRIS', 'RELAX', 'sleep', 'IForKETO',
        'drinkfood', 'flaxseed', 'spirulina', 'lionsmane', 'pickles',
        'fishoilord3', 'water', 'coffeex2', 'noA', 'warmup', 'stretching',
        'workout', 'CODE', 'ENG', 'DE', 'FR', 'UKR',
    ]
    CONDITIONS = {
        'TRUE': [
            'SUNWALK', 'MED', 'TETRIS', 'RELAX',
            'drinkfood', 'flaxseed', 'spirulina', 'lionsmane', 'pickles',
            'fishoilord3', 'water', 'coffeex2', 'warmup', 'stretching',
            'CODE', 'ENG', 'DE', 'FR', 'UKR',
        ],
        'ZERO': [
            'noA',
        ],
        'MINIMUM': {
            'sleep': 7, 'IForKETO': 14,
        },
        'NONEMPTYSTR': [
            'workout',
        ],
    }

    class Meta:
        proxy = True
        verbose_name = "TODO 2023"
        verbose_name_plural = "TODOs 2023"


class TODOList2022Manager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(daydate__year="2022")
        return qs


class TODOList2022(TODOList):
    objects = TODOList2023Manager()

    # INFO_FIELDS = [
    #     'comments',
    #     'awareness', 'happiness', 'openness', 'focus',
    #     'anger', 'fear', 'emptiness', 'chaos',
    # ]
    # TODO_FIELDS = [
    #     'SUNWALK', 'MED', 'TETRIS', 'RELAX', 'sleep', 'IForKETO',
    #     'drinkfood', 'flaxseed', 'spirulina', 'lionsmane', 'pickles',
    #     'fishoilord3', 'water', 'coffeex2', 'noA', 'warmup', 'stretching',
    #     'workout', 'CODE', 'ENG', 'DE', 'FR', 'UKR',
    # ]
    # CONDITIONS = {
    #     'TRUE': [
    #         'SUNWALK', 'MED', 'TETRIS', 'RELAX',
    #         'drinkfood', 'flaxseed', 'spirulina', 'lionsmane', 'pickles',
    #         'fishoilord3', 'water', 'coffeex2', 'warmup', 'stretching',
    #         'CODE', 'ENG', 'DE', 'FR', 'UKR',
    #     ],
    #     'ZERO': [
    #         'noA',
    #     ],
    #     'MINIMUM': {
    #         'sleep': 7, 'IForKETO': 14,
    #     },
    #     'NONEMPTYSTR': [
    #         'workout',
    #     ],
    # }
    
    class Meta:
        proxy = True
        verbose_name = "TODO 2022"
        verbose_name_plural = "TODOs 2022"


# =============================================================================


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