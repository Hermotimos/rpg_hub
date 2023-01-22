from statistics import mean
from typing import List

from django import forms
from django.contrib import admin
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from _todos.models import TODOList2023, Food


# TODO separate conditions for separate years
#   achieve years via proxies: 2020 filter on daydate
#   each year can have different list_display (TODOList) and completion criteria


class TODOListAdmin(admin.ModelAdmin):
    CONDITIONS = {}
    
    formfield_overrides = {
        models.DecimalField: {'widget': forms.NumberInput(attrs={'style': 'width:55px'})},
        models.TextField: {'widget': forms.Textarea(attrs={'rows': 2, 'cols': 25})},
    }

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

    def completion(self, obj):
        colors = {
            range(0, 25): "#ff0000",
            range(26, 50): "#ffa700",
            range(51, 75): "#2cba00",
            range(76, 100): "#007000",
        }
        
        def get_color(val):
            for val_range, code in colors.items():
                if val in val_range:
                    return code
                
        def value(field_name) -> List[str]:
            return getattr(obj, field_name)
        
        def istrue_cnt() -> int:
            return sum(
                value(f) for f in self.CONDITIONS['TRUE']
            )
            
        def iszero_cnt() -> int:
            return sum(
                value(f) == 0 for f in self.CONDITIONS['ZERO']
            )
            
        def ismin_cnt() -> int:
            return sum(
                value(k) >= v for k, v in self.CONDITIONS['MINIMUM'].items()
            )
        
        def isnonempty_cnt() -> int:
            return sum(
                value(f) != "" for f in self.CONDITIONS['NONEMPTYSTR']
            )
        
        sum_completed = istrue_cnt() + iszero_cnt() + ismin_cnt() + isnonempty_cnt()
        sum_todo = sum(len(f) for f in self.CONDITIONS.values())
        res = int(round(sum_completed / sum_todo * 100, 0))
        
        return format_html(f'<b style="color: {get_color(res)}">{res} %</b>')
        
        
@admin.register(TODOList2023)
class TODOList2023Admin(TODOListAdmin):
    list_display = [
        'daydate', 'SUNWALK', 'MED', 'TETRIS', 'RELAX', 'sleep', 'IForKETO',
        'drinkfood', 'flaxseed', 'spirulina', 'lionsmane', 'pickles',
        'fishoilord3', 'water', 'coffeex2', 'noA', 'warmup', 'stretching',
        'workout', 'CODE', 'ENG', 'DE', 'FR', 'UKR',
        'awareness', 'happiness', 'openness', 'focus',
        'anger', 'fear', 'emptiness', 'chaos', 'res',
        'comments', 'completion',
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
    
    
@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'fat', 'protein', 'carbs', 'fiber']
    list_editable = ['name', 'fat', 'protein', 'carbs', 'fiber']
    list_per_page = 1000
    