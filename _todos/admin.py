from statistics import mean
from django.utils.safestring import mark_safe
from django import forms
from django.contrib import admin
from django.db import models

from _todos.models import TODOList


@admin.register(TODOList)
class TODOListAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.DecimalField: {'widget': forms.NumberInput(attrs={'size': 5})},
        models.TextField: {'widget': forms.Textarea(attrs={'rows': 2, 'cols': 20})},
    }
    list_display = [
        'daydate', 'SUNWALK', 'MED', 'TETRIS', 'RELAX', 'sleep', 'IForKETO',
        'drinkfood', 'flaxseed', 'spirulina', 'lionsmane', 'pickles',
        'fishoilord3', 'water', 'coffeex2', 'noA', 'warmup', 'stretching',
        'workout', 'CODE', 'ENG', 'DE', 'FR', 'UKR',
        'awareness', 'happiness', 'openness', 'focus',
        'anger', 'fear', 'emptiness', 'chaos', 'res',
        'comments',
    ]
    list_editable = [
        'SUNWALK', 'MED', 'TETRIS', 'RELAX', 'sleep', 'IForKETO',
        'drinkfood', 'flaxseed', 'spirulina', 'lionsmane', 'pickles',
        'fishoilord3', 'water', 'coffeex2', 'noA', 'warmup', 'stretching',
        'workout', 'CODE', 'ENG', 'DE', 'FR', 'UKR',
        'awareness', 'happiness', 'openness', 'focus',
        'anger', 'fear', 'emptiness', 'chaos',
        'comments',
    ]

    class Media:
        css = {
            'all': ('/static/css/todos_admin.css',)
        }

    def res(self, obj):
        try:
            sum_plus = mean([obj.awareness, obj.happiness, obj.openness, obj.focus])
            sum_minus = mean([obj.anger, obj.fear, obj.emptiness, obj.chaos])
            res = sum_plus - sum_minus

            if res < 1.1:
                color = "red"
            elif res < 2.1:
                color = "gold"
            elif res < 3.1:
                color = "deepskyblue"
            elif res < 4.1:
                color = "indigo"
            else:
                color = "black"
                
            return mark_safe(f'<span style="color: {color}"><b>{res}</b></span>')
        
        except TypeError:
            return "-"
