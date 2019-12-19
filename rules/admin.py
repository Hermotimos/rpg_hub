from django.contrib import admin
from django.forms import Textarea
from django.db import models
from rules.models import Skill, Synergy, CharacterClass, CharacterProfession, EliteClass, EliteProfession, \
    WeaponClass, WeaponType, PlateType, ShieldType


class SkillAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'tested_trait', 'description', 'lvl_0', 'lvl_1', 'lvl_2', 'lvl_3', 'image']
    list_editable = ['name', 'description', 'tested_trait', 'lvl_0', 'lvl_1', 'lvl_2', 'lvl_3', 'image']
    search_fields = ['name', 'description', 'lvl_0', 'lvl_1', 'lvl_2', 'lvl_3']

    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 2, 'cols': 10})},
        models.TextField: {'widget': Textarea(attrs={'rows': 10, 'cols': 30})},
    }


class SynergyAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'lvl_1', 'lvl_2', 'lvl_3']
    list_editable = ['name', 'lvl_1', 'lvl_2', 'lvl_3']
    search_fields = ['name', 'lvl_1', 'lvl_2', 'lvl_3']

    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 3, 'cols': 10})},
        models.TextField: {'widget': Textarea(attrs={'rows': 10, 'cols': 30})},
    }


class CharacterProfessionInline(admin.TabularInline):
    model = CharacterProfession
    extra = 2


class CharacterProfessionAdmin(admin.ModelAdmin):
    list_display = ['name', 'character_class', 'description', 'start_perks']
    list_editable = ['description', 'start_perks']
    search_fields = ['name', 'description', 'start_perks']


class CharacterClassAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    list_editable = ['description']
    inlines = [CharacterProfessionInline]
    search_fields = ['name', 'description']


class EliteProfessionInline(admin.TabularInline):
    model = EliteProfession
    extra = 2


class EliteProfessionAdmin(admin.ModelAdmin):
    list_display = ['name', 'elite_class', 'description', 'start_perks']
    list_editable = ['description', 'start_perks']
    search_fields = ['name', 'description', 'start_perks']


class EliteClassAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    list_editable = ['description']
    inlines = [EliteProfessionInline]
    search_fields = ['name', 'description']


class WeaponTypeInline(admin.TabularInline):
    model = WeaponType
    extra = 2

    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 25})},
        models.CharField: {'widget': Textarea(attrs={'rows': 1, 'cols': 5})},
    }


class WeaponClassAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    list_editable = ['description']
    inlines = [WeaponTypeInline, ]
    search_fields = ['name', 'description']

    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 2, 'cols': 100})},
    }


class WeaponTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    list_editable = ['description']
    search_fields = ['name', 'description']

    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 2, 'cols': 100})},
    }


class PlateTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    list_editable = ['description']
    search_fields = ['name', 'description']

    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 2, 'cols': 100})},
    }


class ShieldTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    list_editable = ['description']
    search_fields = ['name', 'description']

    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 2, 'cols': 100})},
    }


admin.site.register(Skill, SkillAdmin)
admin.site.register(Synergy, SynergyAdmin)
admin.site.register(CharacterClass, CharacterClassAdmin)
admin.site.register(CharacterProfession, CharacterProfessionAdmin)
admin.site.register(EliteClass, EliteClassAdmin)
admin.site.register(EliteProfession, EliteProfessionAdmin)
admin.site.register(WeaponClass, WeaponClassAdmin)
admin.site.register(WeaponType, WeaponTypeAdmin)
admin.site.register(PlateType, PlateTypeAdmin)
admin.site.register(ShieldType, ShieldTypeAdmin)
