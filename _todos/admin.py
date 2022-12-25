from django import forms
from django.contrib import admin
from django.db import models

from _todos.models import TODOList


@admin.register(TODOList)
class TODOListAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.DecimalField: {'widget': forms.NumberInput(attrs={'size': 6})},
        models.TextField: {'widget': forms.Textarea(attrs={'rows': 1, 'cols': 15})},
    }
    list_display = [
        'daydate', 'SUNWALK', 'MED', 'TETRIS', 'RELAX', 'sleep', 'IForKETO',
        'drinkfood', 'flaxseed', 'spirulina', 'lionsmane', 'pickles',
        'fishoilord3', 'water', 'coffeex2', 'noA', 'warmup', 'stretching',
        'workout', 'CODE', 'ENG', 'DE', 'FR', 'UKR',
        'awareness', 'happiness', 'openness', 'focus',
        'anger', 'fear', 'emptiness', 'chaos',
    ]
    list_editable = [
        'SUNWALK', 'MED', 'TETRIS', 'RELAX', 'sleep', 'IForKETO',
        'drinkfood', 'flaxseed', 'spirulina', 'lionsmane', 'pickles',
        'fishoilord3', 'water', 'coffeex2', 'noA', 'warmup', 'stretching',
        'workout', 'CODE', 'ENG', 'DE', 'FR', 'UKR',
        'awareness', 'happiness', 'openness', 'focus',
        'anger', 'fear', 'emptiness', 'chaos',
    ]

    class Media:
        css = {
            'all': ('/static/css/admin.css',)
        }
