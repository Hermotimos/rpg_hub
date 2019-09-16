from django.contrib import admin
from django.forms import Textarea
from django.db import models
from rules.models import Skill, Synergy, CharacterClass, CharacterProfession, EliteProfession


class CharacterProfessionAdmin(admin.ModelAdmin):
    list_display = ['name', 'character_class', 'description', 'start_perks']
    list_editable = ['description', 'start_perks']


class SkillAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'tested_trait', 'description', 'lvl_0', 'lvl_1', 'lvl_2', 'lvl_3', 'image']
    list_editable = ['name', 'description', 'tested_trait', 'lvl_0', 'lvl_1', 'lvl_2', 'lvl_3', 'image']

    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 2, 'cols': 10})},
        models.TextField: {'widget': Textarea(attrs={'rows': 10, 'cols': 30})},
    }


class SynergyAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'lvl_1', 'lvl_2', 'lvl_3']
    list_editable = ['name', 'lvl_1', 'lvl_2', 'lvl_3']

    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 2, 'cols': 10})},
        models.TextField: {'widget': Textarea(attrs={'rows': 10, 'cols': 30})},
    }


admin.site.register(Skill, SkillAdmin)
admin.site.register(Synergy, SynergyAdmin)
admin.site.register(CharacterClass)
admin.site.register(CharacterProfession, CharacterProfessionAdmin)
admin.site.register(EliteProfession)
