from statistics import mean

from django import forms
from django.contrib import admin
from django.db import models
from django.utils.safestring import mark_safe, SafeString

from _todos.admin_utils import compl_daily, format_compl, compl_monthly
from _todos.models import TODOList2023, TODOList2022, Food, Month


@admin.register(Month)
class MonthAdmin(admin.ModelAdmin):
    list_display = ['monthdate', 'completion']
    
    def completion(self, obj):
        try:
            return format_compl(compl_monthly(obj))
        except ZeroDivisionError:
            pass
           
    
class TODOListAdmin(admin.ModelAdmin):
    """An abstract ModelAdmin that serves as template via subclassing."""
    ADMIN_FIELDS_1 = ['daydate']
    ADMIN_FIELDS_2 = ['res', 'completion']
    formfield_overrides = {
        models.PositiveSmallIntegerField: {'widget': forms.NumberInput(attrs={'style': 'width:35px'})},
        models.DecimalField: {'widget': forms.NumberInput(attrs={'style': 'width:55px'})},
        models.TextField: {'widget': forms.Textarea(attrs={'rows': 2, 'cols': 25})},
    }

    class Media:
        css = {
            'all': ('/static/css/todos_admin.css',)
        }

    def res(self, obj) -> str:
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

    def completion(self, obj) -> SafeString:
        return format_compl(compl_daily(obj))
        
        
@admin.register(TODOList2023)
class TODOList2023Admin(TODOListAdmin):
    list_display = [
        *TODOListAdmin.ADMIN_FIELDS_1,
        *TODOList2023.TODO_FIELDS,
        *TODOList2023.INFO_FIELDS,
        *TODOListAdmin.ADMIN_FIELDS_2,
    ]
    list_editable = [
        *TODOList2023.TODO_FIELDS,
        *TODOList2023.INFO_FIELDS,
    ]


@admin.register(TODOList2022)
class TODOList2023Admin(TODOListAdmin):
    formfield_overrides = {
        models.PositiveSmallIntegerField: {'widget': forms.NumberInput(attrs={'style': 'width:35px'})},
        models.DecimalField: {'widget': forms.NumberInput(attrs={'style': 'width:55px'})},
        models.TextField: {'widget': forms.Textarea(attrs={'rows': 2, 'cols': 15})},
    }
    list_display = [
        *TODOListAdmin.ADMIN_FIELDS_1,
        *TODOList2022.TODO_FIELDS,
        *TODOList2022.INFO_FIELDS,
        *TODOListAdmin.ADMIN_FIELDS_2,
    ]
    list_editable = [
        *TODOList2022.TODO_FIELDS,
        *TODOList2022.INFO_FIELDS,
    ]


@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'fat', 'protein', 'carbs', 'fiber']
    list_editable = ['name', 'fat', 'protein', 'carbs', 'fiber']
    list_per_page = 1000
    