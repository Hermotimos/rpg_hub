from django.contrib import admin
from django.forms import Textarea
from django.db import models
from rules.models import Skill, Synergy


class SkillAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'tested_trait', 'description', 'lvl_0', 'lvl_1', 'lvl_2', 'lvl_3', 'image']
    list_editable = ['name', 'description', 'tested_trait', 'lvl_0', 'lvl_1', 'lvl_2', 'lvl_3', 'image']

    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 1, 'cols': 8})},
        models.TextField: {'widget': Textarea(attrs={'rows': 10, 'cols': 30})},
    }


class SynergyAdmin(admin.ModelAdmin):
    list_display = ['name', 'lvl_1', 'lvl_2', 'lvl_3']
    list_editable = ['lvl_1', 'lvl_2', 'lvl_3']

    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 1, 'cols': 8})},
        models.TextField: {'widget': Textarea(attrs={'rows': 10, 'cols': 30})},
    }


admin.site.register(Skill, SkillAdmin)
admin.site.register(Synergy, SynergyAdmin)
