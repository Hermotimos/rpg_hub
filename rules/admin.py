from django.contrib import admin
from django.forms import Textarea
from django.db import models
from rules.models import Skill, Synergy


class SkillAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'tested_trait', 'description', 'lvl0_desc', 'lvl1_desc', 'lvl2_desc', 'lvl3_desc',
                    'image']
    list_editable = ['name', 'description', 'tested_trait', 'lvl0_desc', 'lvl1_desc', 'lvl2_desc', 'lvl3_desc', 'image']

    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 1, 'cols': 8})},
        models.TextField: {'widget': Textarea(attrs={'rows': 10, 'cols': 30})},
    }


class SynergyAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'lvl1_desc', 'lvl2_desc', 'lvl3_desc',
                    'image']
    list_editable = ['description', 'lvl1_desc', 'lvl2_desc', 'lvl3_desc', 'image']

    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 1, 'cols': 8})},
        models.TextField: {'widget': Textarea(attrs={'rows': 10, 'cols': 30})},
    }

admin.site.register(Skill, SkillAdmin)
admin.site.register(Synergy, SynergyAdmin)