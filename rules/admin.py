from django.contrib import admin
from django.db import models
from django.forms import Textarea

from rpg_project.utils import formfield_for_dbfield_cached
from rules.admin_filters import SkillLevelFilter, SynergyLevelFilter
from rules.admin_forms import (
    Form1, Form2,
    PerkAdminForm,
    SkillAdminForm, SkillLevelAdminForm,
    SynergyAdminForm, SynergyLevelAdminForm
)
from rules.models import (
    SkillGroup, SkillKind, SkillType,
    Skill, SkillLevel, Synergy, SynergyLevel, BooksSkill, TheologySkill,
    Perk, Modifier, Factor, RulesComment,
    Profession, EliteProfession, Klass, EliteKlass,
    WeaponType, Weapon, Plate, Shield,
)


# =============================================================================


class FactorAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    list_editable = ['name']


class ModifierAdmin(admin.ModelAdmin):
    # inlines = [ConditionalModifierInline]
    list_display = ['id', 'sign', 'value_number', 'value_percent', 'value_text', 'factor', 'condition']
    list_editable = ['sign', 'value_number', 'value_percent', 'value_text', 'factor', 'condition']
    list_select_related = ['factor']

    def formfield_for_dbfield(self, db_field, **kwargs):
        fields = [
            'factor',
        ]
        return formfield_for_dbfield_cached(self, db_field, fields, **kwargs)


class RulesCommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'text']
    list_editable = ['text']


class PerkAdmin(admin.ModelAdmin):
    form = PerkAdminForm
    list_display = ['id', 'name', 'description', 'cost']
    list_editable = ['name', 'description', 'cost']

    
# =============================================================================


class SkillKindAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    list_editable = ['name']


class SkillTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    list_editable = ['name']


class SkillGroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'type']
    list_editable = ['name', 'type']


class SkillLevelInline(admin.TabularInline):
    model = SkillLevel
    extra = 4


class SynergyLevelInline(admin.TabularInline):
    model = SynergyLevel
    extra = 1
    
    
class SkillAdmin(admin.ModelAdmin):
    form = SkillAdminForm
    inlines = [SkillLevelInline]
    list_display = ['id', 'name', 'tested_trait', 'image', 'group']
    list_editable = ['name', 'tested_trait', 'image', 'group']
    list_filter = ['types', 'group']
    list_select_related = ['group__type']
    search_fields = ['name']
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        fields = [
            'group',
        ]
        return formfield_for_dbfield_cached(self, db_field, fields, **kwargs)


class SynergyAdmin(admin.ModelAdmin):
    form = SynergyAdminForm
    formfield_overrides = {
        models.CharField: {
            'widget': Textarea(attrs={'rows': 3, 'cols': 10})},
        models.TextField: {
            'widget': Textarea(attrs={'rows': 10, 'cols': 30})},
    }
    inlines = [SynergyLevelInline]
    list_display = ['id', 'name']
    list_editable = ['name']
    search_fields = ['name']


class SkillLevelAdmin(admin.ModelAdmin):
    form = SkillLevelAdminForm
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 8, 'cols': 80})},
    }

    list_display = ['name', 'description']
    list_editable = ['description']
    list_filter = [SkillLevelFilter]
    list_select_related = ['skill']
    search_fields = ['level', 'description']

    def name(self, obj):
        return f'{str(obj.skill.name)} [{obj.level}]'


class SynergyLevelAdmin(admin.ModelAdmin):
    form = SynergyLevelAdminForm
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 8, 'cols': 80})},
    }

    list_display = ['name', 'description']
    list_editable = ['description']
    list_filter = [SynergyLevelFilter]
    list_select_related = ['synergy']
    search_fields = ['level', 'description']

    def name(self, obj):
        return f'{str(obj.synergy.name)} [{obj.level}]'


# =============================================================================


class KlassInline(admin.TabularInline):
    model = Klass
    extra = 2

    fields = ['name', 'description', 'start_perks', 'allowed_profiles']
    form = Form1
    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 1, 'cols': 10})},
        models.TextField: {'widget': Textarea(attrs={'rows': 15, 'cols': 40})},
    }


class KlassAdmin(admin.ModelAdmin):
    form = Form1
    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 1, 'cols': 10})},
        models.TextField: {'widget': Textarea(attrs={'rows': 10, 'cols': 60})},
    }
    list_display = ['name', 'profession', 'description', 'start_perks']
    list_editable = ['description', 'start_perks']
    search_fields = ['name', 'description', 'start_perks']


class ProfessionAdmin(admin.ModelAdmin):
    inlines = [KlassInline]
    list_display = ['name', 'description']
    list_editable = ['description']
    search_fields = ['name', 'description']


class EliteKlassInline(admin.TabularInline):
    model = EliteKlass
    extra = 2

    form = Form1
    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 1, 'cols': 10})},
        models.TextField: {'widget': Textarea(attrs={'rows': 15, 'cols': 40})},
    }


class EliteKlassAdmin(admin.ModelAdmin):
    form = Form1
    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 1, 'cols': 10})},
        models.TextField: {'widget': Textarea(attrs={'rows': 10, 'cols': 60})},
    }
    list_display = ['name', 'elite_profession', 'description', 'start_perks']
    list_editable = ['description', 'start_perks']
    search_fields = ['name', 'description', 'start_perks']


class EliteProfessionAdmin(admin.ModelAdmin):
    form = Form1
    inlines = [EliteKlassInline]
    list_display = ['name', 'description']
    list_editable = ['description']
    search_fields = ['name', 'description']


# =============================================================================


class WeaponInline(admin.TabularInline):
    model = Weapon
    extra = 2

    form = Form2
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 25})},
        models.CharField: {'widget': Textarea(attrs={'rows': 1, 'cols': 5})},
    }


class WeaponTypeAdmin(admin.ModelAdmin):
    inlines = [WeaponInline]
    list_display = ['name']


class WeaponAdmin(admin.ModelAdmin):
    form = Form2
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 2, 'cols': 100})},
    }
    list_display = ['name', 'description']
    list_editable = ['description']
    list_filter = ['weapon_type']
    search_fields = ['name', 'description']

    def formfield_for_dbfield(self, db_field, **kwargs):
        fields = [
            'allowed_profiles',
            'pictures',
        ]
        return formfield_for_dbfield_cached(self, db_field, fields, **kwargs)


class PlateAdmin(admin.ModelAdmin):
    form = Form2
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 2, 'cols': 100})},
    }
    list_display = ['name', 'description']
    list_editable = ['description']
    search_fields = ['name', 'description']


class ShieldTypeAdmin(admin.ModelAdmin):
    form = Form2
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 2, 'cols': 100})},
    }
    list_display = ['name', 'description']
    list_editable = ['description']
    search_fields = ['name', 'description']


# =============================================================================

admin.site.register(Factor, FactorAdmin)
admin.site.register(Modifier, ModifierAdmin)
admin.site.register(Perk, PerkAdmin)
admin.site.register(RulesComment, RulesCommentAdmin)

admin.site.register(SkillType, SkillTypeAdmin)
admin.site.register(SkillKind, SkillKindAdmin)
admin.site.register(SkillGroup, SkillGroupAdmin)
admin.site.register(Skill, SkillAdmin)
admin.site.register(BooksSkill, SkillAdmin)
admin.site.register(TheologySkill, SkillAdmin)
admin.site.register(SkillLevel, SkillLevelAdmin)
admin.site.register(Synergy, SynergyAdmin)
admin.site.register(SynergyLevel, SynergyLevelAdmin)

admin.site.register(Profession, ProfessionAdmin)
admin.site.register(Klass, KlassAdmin)
admin.site.register(EliteProfession, EliteProfessionAdmin)
admin.site.register(EliteKlass, EliteKlassAdmin)

admin.site.register(WeaponType, WeaponTypeAdmin)
admin.site.register(Weapon, WeaponAdmin)
admin.site.register(Plate, PlateAdmin)
admin.site.register(Shield, ShieldTypeAdmin)
