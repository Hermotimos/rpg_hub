from django.contrib import admin
from django.db.models import TextField, ForeignKey, CharField
from django.forms import Textarea, Select

from rpg_project.utils import formfield_for_dbfield_cached
from rules.admin_filters import SkillLevelFilter, SynergyLevelFilter
from rules.models import (
    SkillGroup, SkillKind, SkillType,
    Skill, SkillLevel, Synergy, SynergyLevel, BooksSkill, TheologySkill,
    Perk, Modifier, Factor, RulesComment, Condition, CombatType,
    ConditionalModifier,
    Profession, EliteProfession, Klass, EliteKlass,
    WeaponType, Weapon, Plate, Shield,
)


# =============================================================================


@admin.register(Factor)
class FactorAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    list_editable = ['name']

   
@admin.register(Modifier)
class ModifierAdmin(admin.ModelAdmin):
    empty_value_display = ''
    list_display = ['id', 'sign', 'value_number', 'value_percent', 'value_text', 'factor']
    list_editable = ['sign', 'value_number', 'value_percent', 'value_text', 'factor']
    list_filter = ['factor', 'sign']
    list_select_related = ['factor']
    radio_fields = {"sign": admin.VERTICAL}
    readonly_fields = ['overview']
    search_fields = ['value_number', 'value_percent', 'value_text', 'factor']

    def formfield_for_dbfield(self, db_field, **kwargs):
        fields = [
            'factor',
        ]
        return formfield_for_dbfield_cached(self, db_field, fields, **kwargs)


@admin.register(RulesComment)
class RulesCommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'text']
    list_editable = ['text']


@admin.register(Perk)
class PerkAdmin(admin.ModelAdmin):
    filter_horizontal = ['conditional_modifiers', 'comments']
    list_display = ['id', 'name', 'description', 'cost']
    list_editable = ['name', 'description', 'cost']
    list_filter = ['skill_levels__skill']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.prefetch_related(
            'conditional_modifiers__modifier__factor',
            'conditional_modifiers__combat_types',
            'conditional_modifiers__conditions',
            'comments')
        return qs

    
@admin.register(Condition)
class ConditionAdmin(admin.ModelAdmin):
    list_display = ['id', 'text']
    list_editable = ['text']


@admin.register(ConditionalModifier)
class ConditionalModifierAdmin(admin.ModelAdmin):
    filter_horizontal = ['combat_types', 'conditions']
    list_display = ['__str__']
    readonly_fields = ['overview']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related('modifier__factor')
        qs = qs.prefetch_related('combat_types', 'conditions')
        return qs


@admin.register(CombatType)
class CombatTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    list_editable = ['name']

    
# =============================================================================


@admin.register(SkillKind)
class SkillKindAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    list_editable = ['name']


@admin.register(SkillType)
class SkillTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    list_editable = ['name']


@admin.register(SkillGroup)
class SkillGroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'type']
    list_editable = ['name', 'type']


class SkillLevelInline(admin.TabularInline):
    model = SkillLevel
    extra = 4
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        fields = [
            'perks',
            'acquired_by',
        ]
        return formfield_for_dbfield_cached(self, db_field, fields, **kwargs)
    
    
@admin.register(Skill, BooksSkill, TheologySkill)
class SkillAdmin(admin.ModelAdmin):
    fields = ['name', 'tested_trait', 'image', 'group', 'types', 'allowees']
    filter_horizontal = ['allowees', 'types']
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


class SynergyLevelInline(admin.TabularInline):
    model = SynergyLevel
    extra = 1
    filter_horizontal = ['skill_levels', 'perks']
    formfield_overrides = {
        TextField: {'widget': Textarea(attrs={'rows': 20, 'cols': 30})},
    }
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        fields = [
            'skill_levels',
        ]
        return formfield_for_dbfield_cached(self, db_field, fields, **kwargs)


@admin.register(Synergy)
class SynergyAdmin(admin.ModelAdmin):
    filter_horizontal = ['skills']
    formfield_overrides = {
        CharField: {'widget': Textarea(attrs={'rows': 3, 'cols': 10})},
        TextField: {'widget': Textarea(attrs={'rows': 10, 'cols': 30})},
    }
    inlines = [SynergyLevelInline]
    list_display = ['id', 'name']
    list_editable = ['name']
    search_fields = ['name']

    # def formfield_for_dbfield(self, db_field, **kwargs):
    #     fields = [
    #         'skill_levels',
    #         'skill_levels__skill',
    #         'skills',
    #     ]
    #     return formfield_for_dbfield_cached(self, db_field, fields, **kwargs)


@admin.register(SkillLevel)
class SkillLevelAdmin(admin.ModelAdmin):
    filter_horizontal = ['acquired_by', 'perks']
    formfield_overrides = {
        TextField: {'widget': Textarea(attrs={'rows': 8, 'cols': 80})},
    }
    list_display = ['name', 'description']
    list_editable = ['description']
    list_filter = [SkillLevelFilter]
    list_select_related = ['skill']
    search_fields = ['level', 'description']

    def name(self, obj):
        return f'{str(obj.skill.name)} [{obj.level}]'


@admin.register(SynergyLevel)
class SynergyLevelAdmin(admin.ModelAdmin):
    filter_horizontal = ['acquired_by', 'perks']
    formfield_overrides = {
        TextField: {'widget': Textarea(attrs={'rows': 8, 'cols': 80})},
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
    fields = ['name', 'description', 'start_perks', 'allowees']
    filter_horizontal = ['allowees']
    formfield_overrides = {
        CharField: {'widget': Textarea(attrs={'rows': 1, 'cols': 10})},
        TextField: {'widget': Textarea(attrs={'rows': 15, 'cols': 40})},
    }


@admin.register(Klass)
class KlassAdmin(admin.ModelAdmin):
    filter_horizontal = ['allowees']
    formfield_overrides = {
        CharField: {'widget': Textarea(attrs={'rows': 1, 'cols': 10})},
        TextField: {'widget': Textarea(attrs={'rows': 10, 'cols': 60})},
    }
    list_display = ['name', 'profession', 'description', 'start_perks']
    list_editable = ['description', 'start_perks']
    search_fields = ['name', 'description', 'start_perks']


@admin.register(Profession)
class ProfessionAdmin(admin.ModelAdmin):
    inlines = [KlassInline]
    list_display = ['name', 'description']
    list_editable = ['description']
    search_fields = ['name', 'description']


class EliteKlassInline(admin.TabularInline):
    model = EliteKlass
    extra = 2
    filter_horizontal = ['allowees']
    formfield_overrides = {
        CharField: {'widget': Textarea(attrs={'rows': 1, 'cols': 10})},
        TextField: {'widget': Textarea(attrs={'rows': 15, 'cols': 40})},
    }


@admin.register(EliteKlass)
class EliteKlassAdmin(admin.ModelAdmin):
    filter_horizontal = ['allowees']
    formfield_overrides = {
        CharField: {'widget': Textarea(attrs={'rows': 1, 'cols': 10})},
        TextField: {'widget': Textarea(attrs={'rows': 10, 'cols': 60})},
    }
    list_display = ['name', 'elite_profession', 'description', 'start_perks']
    list_editable = ['description', 'start_perks']
    search_fields = ['name', 'description', 'start_perks']


@admin.register(EliteProfession)
class EliteProfessionAdmin(admin.ModelAdmin):
    filter_horizontal = ['allowees']
    inlines = [EliteKlassInline]
    list_display = ['name', 'description']
    list_editable = ['description']
    search_fields = ['name', 'description']


# =============================================================================


class WeaponInline(admin.TabularInline):
    model = Weapon
    extra = 2
    formfield_overrides = {
        TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 25})},
        CharField: {'widget': Textarea(attrs={'rows': 1, 'cols': 5})},
    }


@admin.register(WeaponType)
class WeaponTypeAdmin(admin.ModelAdmin):
    inlines = [WeaponInline]
    list_display = ['name']


@admin.register(Weapon)
class WeaponAdmin(admin.ModelAdmin):
    filter_horizontal = ['allowees']
    formfield_overrides = {
        TextField: {'widget': Textarea(attrs={'rows': 2, 'cols': 100})},
    }
    list_display = ['name', 'description']
    list_editable = ['description']
    list_filter = ['weapon_type']
    search_fields = ['name', 'description']

    def formfield_for_dbfield(self, db_field, **kwargs):
        fields = [
            'allowees',
            'picture_set',
        ]
        return formfield_for_dbfield_cached(self, db_field, fields, **kwargs)


@admin.register(Plate)
class PlateAdmin(admin.ModelAdmin):
    filter_horizontal = ['allowees']
    formfield_overrides = {
        TextField: {'widget': Textarea(attrs={'rows': 2, 'cols': 100})},
    }
    list_display = ['name', 'description', 'comment']
    list_editable = ['description', 'comment']
    search_fields = ['name', 'description', 'comment']


@admin.register(Shield)
class ShieldAdmin(admin.ModelAdmin):
    filter_horizontal = ['allowees']
    formfield_overrides = {
        TextField: {'widget': Textarea(attrs={'rows': 2, 'cols': 50})},
        ForeignKey: {'widget': Select(attrs={'style': 'width:180px'})},
    }
    list_display = ['id', 'name', 'armor_class_bonus', 'weight', 'description', 'picture_set', 'comment']
    list_editable = ['name', 'armor_class_bonus', 'weight', 'description', 'picture_set', 'comment']
    search_fields = ['name', 'description', 'comment']
    list_select_related = True

    # def formfield_for_dbfield(self, db_field, **kwargs):
    #     fields = [
    #         'allowees',
    #         'picture_set',
    #     ]
    #     return formfield_for_dbfield_cached(self, db_field, fields, **kwargs)
    #
