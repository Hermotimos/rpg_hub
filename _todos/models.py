import datetime

from django.db.models import Model, DateField, BooleanField, DecimalField, \
    TextField, PositiveSmallIntegerField


class TODOList(Model):
    MARKS = [
        (0, '0'),
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
    ]
    
    # technical
    daydate = DateField(default=datetime.date.today, unique=True)
    # PSYCHE
    SUNWALK = BooleanField(default=False)
    MED = BooleanField(default=False)
    TETRIS = BooleanField(default=False)
    RELAX = BooleanField(default=False)
    # SOMA
    sleep = DecimalField(max_digits=4, decimal_places=2, default=0)
    IForKETO = DecimalField(max_digits=4, decimal_places=2, default=0)
    drinkfood = BooleanField(default=False)
    # --
    flaxseed = BooleanField(default=False)
    spirulina = BooleanField(default=False)
    lionsmane = BooleanField(default=False)
    pickles = BooleanField(default=False)
    fishoilord3 = BooleanField(default=False)
    water = BooleanField(default=False)
    # --
    coffeex2 = BooleanField(default=False)
    noA = DecimalField(max_digits=4, decimal_places=2, default=0)
    # --
    warmup = BooleanField(default=False)
    stretching = BooleanField(default=False)
    workout = TextField(blank=True, null=True)
    # NOOS
    CODE = BooleanField(default=False)
    ENG = BooleanField(default=False)
    DE = BooleanField(default=False)
    FR = BooleanField(default=False)
    UKR = BooleanField(default=False)
    
    # marks
    awareness = PositiveSmallIntegerField(choices=MARKS, null=True, blank=True)
    happiness = PositiveSmallIntegerField(choices=MARKS, null=True, blank=True)
    openness = PositiveSmallIntegerField(choices=MARKS, null=True, blank=True)
    focus = PositiveSmallIntegerField(choices=MARKS, null=True, blank=True)
    anger = PositiveSmallIntegerField(choices=MARKS, null=True, blank=True)
    fear = PositiveSmallIntegerField(choices=MARKS, null=True, blank=True)
    emptiness = PositiveSmallIntegerField(choices=MARKS, null=True, blank=True)
    chaos = PositiveSmallIntegerField(choices=MARKS, null=True, blank=True)
    
    # comments
    comments = TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-daydate']
    
    @property
    def completion(self):
        # TODO
        pass