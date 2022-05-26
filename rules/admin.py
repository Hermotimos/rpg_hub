from django import forms
from django.contrib import admin
from django.db import models

from rpg_project.utils import formfield_with_cache
from rules.admin_filters import SkillLevelFilter, SynergyLevelFilter
from rules.models import (
    SkillGroup, SkillKind, SkillType,
    Skill, SkillLevel, Synergy, SynergyLevel, BooksSkill, TheologySkill,
    Perk, Modifier, Factor, RulesComment, Condition, CombatType,
    ConditionalModifier,
    Profession, SubProfession,
    WeaponType, Weapon, Plate, Shield,
)
from users.models import Profile


# -----------------------------------------------------------------------------


@admin.register(Factor)
class FactorAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    list_editable = ['name']

   
@admin.register(Modifier)
class ModifierAdmin(admin.ModelAdmin):
    empty_value_display = ''
    list_display = [
        'id', 'sign', 'value_number', 'value_percent', 'value_text', 'factor'
    ]
    list_editable = [
        'sign', 'value_number', 'value_percent', 'value_text', 'factor'
    ]
    list_filter = ['factor', 'sign']
    list_select_related = ['factor']
    radio_fields = {"sign": admin.VERTICAL}
    readonly_fields = ['overview']
    search_fields = ['value_number', 'value_percent', 'value_text', 'factor']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        for field in [
            'factor',
        ]:
            if db_field.name == field:
                formfield = formfield_with_cache(field, formfield, request)
        return formfield


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

    
# -----------------------------------------------------------------------------


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
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        for field in [
            'perks',
            'acquired_by',
        ]:
            if db_field.name == field:
                formfield = formfield_with_cache(field, formfield, request)
        return formfield

    
@admin.register(Skill, BooksSkill, TheologySkill)
class SkillAdmin(admin.ModelAdmin):
    fields = [
        'name', 'version_of', 'tested_trait', 'image', 'group', 'types',
        'allowees',
    ]
    filter_horizontal = ['allowees', 'types']
    # inlines = [SkillLevelInline]
    list_display = ['id', 'name', 'version_of', 'tested_trait', 'image', 'group']
    list_editable = ['name', 'tested_trait', 'image', 'group']
    list_filter = ['types', 'group']
    list_select_related = ['group__type']
    search_fields = ['name']
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        for field in [
            'group',
            'version_of',
            # 'shpragis',
        ]:
            if db_field.name == field:
                formfield = formfield_with_cache(field, formfield, request)
        return formfield

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "types":
            kwargs["queryset"] = SkillType.objects.prefetch_related('kinds')
        if db_field.name == "allowees":
            kwargs["queryset"] = Profile.players.select_related('character')
        return super().formfield_for_manytomany(db_field, request, **kwargs)
    

class SynergyLevelInline(admin.TabularInline):
    model = SynergyLevel
    extra = 1
    filter_horizontal = ['skill_levels', 'perks']
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(attrs={'rows': 20, 'cols': 30})},
    }

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        for field in [
            'skill_levels',
        ]:
            if db_field.name == field:
                formfield = formfield_with_cache(field, formfield, request)
        return formfield


@admin.register(Synergy)
class SynergyAdmin(admin.ModelAdmin):
    filter_horizontal = ['skills']
    formfield_overrides = {
        models.CharField: {'widget': forms.Textarea(attrs={'rows': 3, 'cols': 10})},
        models.TextField: {'widget': forms.Textarea(attrs={'rows': 10, 'cols': 30})},
    }
    inlines = [SynergyLevelInline]
    list_display = ['id', 'name']
    list_editable = ['name']
    search_fields = ['name']

    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
    #     for field in [
    #         'skill_levels',
    #         'skill_levels__skill',
    #         'skills',
    #     ]:
    #         if db_field.name == field:
    #             formfield = formfield_with_cache(field, formfield, request)
    #     return formfield


@admin.register(SkillLevel)
class SkillLevelAdmin(admin.ModelAdmin):
    filter_horizontal = ['acquired_by', 'perks']
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(attrs={'rows': 8, 'cols': 80})},
    }
    list_display = ['name', 'description']
    list_editable = ['description']
    list_filter = [SkillLevelFilter]
    list_select_related = ['skill']
    search_fields = ['level', 'description']

    def name(self, obj):
        return f'{str(obj.skill.name)} [{obj.level}]'
    
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "acquired_by":
            kwargs["queryset"] = Profile.objects.select_related('character')
        return super().formfield_for_manytomany(db_field, request, **kwargs)
    

@admin.register(SynergyLevel)
class SynergyLevelAdmin(admin.ModelAdmin):
    filter_horizontal = ['acquired_by', 'perks']
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(attrs={'rows': 8, 'cols': 80})},
    }
    list_display = ['name', 'description']
    list_editable = ['description']
    list_filter = [SynergyLevelFilter]
    list_select_related = ['synergy']
    search_fields = ['level', 'description']

    def name(self, obj):
        return f'{str(obj.synergy.name)} [{obj.level}]'


# -----------------------------------------------------------------------------


class SubProfessionInline(admin.TabularInline):
    model = SubProfession
    extra = 2
    fields = ['name', 'description', 'allowees', 'essential_skills']
    filter_horizontal = ['allowees', 'essential_skills']
    formfield_overrides = {
        models.CharField: {'widget': forms.Textarea(attrs={'rows': 1, 'cols': 10})},
        models.TextField: {'widget': forms.Textarea(attrs={'rows': 15, 'cols': 40})},
    }


@admin.register(Profession)
class ProfessionAdmin(admin.ModelAdmin):
    fields = ['name', 'type', 'description', 'allowees']
    filter_horizontal = ['allowees']
    inlines = [SubProfessionInline]
    list_display = ['name', 'type', 'description']
    list_editable = ['type', 'description']
    list_filter = ['type']
    search_fields = ['name', 'description']
    
    
@admin.register(SubProfession)
class SubProfessionAdmin(admin.ModelAdmin):
    fields = [
        'name', 'profession', 'description', 'essential_skills', 'allowees']
    filter_horizontal = ['allowees', 'essential_skills']
    list_display = ['name', 'profession', 'description']
    list_editable = ['profession', 'description']
    list_filter = ['profession', 'profession__type']
    search_fields = ['name', 'description']
    list_select_related = True
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        for field in [
            'profession',
        ]:
            if db_field.name == field:
                formfield = formfield_with_cache(field, formfield, request)
        return formfield
    
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "essential_skills":
            kwargs["queryset"] = Skill.objects.filter(
                types__kinds__name__in=["Powszechne", "Mentalne"])
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related('profession')
        return qs


# -----------------------------------------------------------------------------


class WeaponInline(admin.TabularInline):
    model = Weapon
    extra = 2
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(attrs={'rows': 1, 'cols': 25})},
        models.CharField: {'widget': forms.Textarea(attrs={'rows': 1, 'cols': 5})},
    }


@admin.register(WeaponType)
class WeaponTypeAdmin(admin.ModelAdmin):
    inlines = [WeaponInline]
    list_display = ['name']


@admin.register(Weapon)
class WeaponAdmin(admin.ModelAdmin):
    filter_horizontal = ['allowees']
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(attrs={'rows': 2, 'cols': 100})},
    }
    list_display = ['name', 'description']
    list_editable = ['description']
    list_filter = ['weapon_type']
    search_fields = ['name', 'description']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        for field in [
            'allowees',
            'picture_set',
        ]:
            if db_field.name == field:
                formfield = formfield_with_cache(field, formfield, request)
        return formfield


@admin.register(Plate)
class PlateAdmin(admin.ModelAdmin):
    filter_horizontal = ['allowees']
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(attrs={'rows': 2, 'cols': 100})},
    }
    list_display = ['name', 'description', 'comment']
    list_editable = ['description', 'comment']
    search_fields = ['name', 'description', 'comment']


@admin.register(Shield)
class ShieldAdmin(admin.ModelAdmin):
    filter_horizontal = ['allowees']
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(attrs={'rows': 2, 'cols': 50})},
        models.ForeignKey: {'widget': forms.Select(attrs={'style': 'width:180px'})},
    }
    list_display = [
        'id', 'name', 'armor_class_bonus', 'weight', 'description',
        'picture_set', 'comment'
    ]
    list_editable = [
        'name', 'armor_class_bonus', 'weight', 'description', 'picture_set',
        'comment'
    ]
    search_fields = ['name', 'description', 'comment']
    list_select_related = True
