from django import forms
from django.contrib import admin
from django.db import models
from django.utils.html import format_html

from rpg_project.utils import formfield_with_cache
from rules.admin_filters import SkillLevelFilter, SynergyLevelFilter
from rules.models import (
    SkillGroup, SkillKind, SkillType,
    Sphragis,
    Skill, SkillLevel, Synergy, SynergyLevel,
    RegularSkill, RegularSkillLevel, RegularSynergy, RegularSynergyLevel,
    MentalSkill, MentalSkillLevel, MentalSynergy, MentalSynergyLevel,
    PriestsSkill, PriestsSkillLevel,
    SorcerersSkill, SorcerersSkillLevel,
    TheurgistsSkill, TheurgistsSkillLevel,
    
    Perk, Modifier, Factor, RulesComment, Condition, CombatType,
    ConditionalModifier,
    Profession, SubProfession,
    DamageType, WeaponType, Plate, Shield,
)


# -----------------------------------------------------------------------------


@admin.register(Factor)
class FactorAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    list_editable = ['name']


@admin.register(Condition)
class ConditionAdmin(admin.ModelAdmin):
    list_display = ['id', 'text']
    list_editable = ['text']


@admin.register(RulesComment)
class RulesCommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'text']
    list_editable = ['text']


@admin.register(CombatType)
class CombatTypeAdmin(admin.ModelAdmin):
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
    search_fields = ['value_number', 'value_percent', 'value_text', 'factor__name']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        for field in [
            'factor',
        ]:
            if db_field.name == field:
                formfield = formfield_with_cache(field, formfield, request)
        return formfield


@admin.register(Perk)
class PerkAdmin(admin.ModelAdmin):
    filter_horizontal = ['conditional_modifiers', 'comments']
    list_display = ['id', 'name', 'description', 'cost']
    list_editable = ['name', 'description', 'cost']
    list_filter = ['skill_levels__skill']
    search_fields = ['name', 'description']

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "conditional_modifiers":
            kwargs["queryset"] = ConditionalModifier.objects.prefetch_related('combat_types')
        return super().formfield_for_manytomany(db_field, request, **kwargs)
    

class ConditionalModifierAdminForm(forms.ModelForm):
    """Custom form for query optimization."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['modifier'].queryset = Modifier.objects.select_related('factor')

    class Meta:
        model = ConditionalModifier
        exclude = []

        
@admin.register(ConditionalModifier)
class ConditionalModifierAdmin(admin.ModelAdmin):
    filter_horizontal = ['combat_types', 'conditions']
    form = ConditionalModifierAdminForm
    list_display = ['__str__', '_perks']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related('modifier__factor')
        qs = qs.prefetch_related('combat_types', 'conditions', 'perks')
        return qs

    def _perks(self, obj):
        perks = " | ".join([p.name for p in obj.perks.all()])
        return format_html(f'<span>{perks}</span>')

    
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


# -----------------------------------------------------------------------------


class RegularSkillLevelInline(admin.TabularInline):
    fields = ['level', 'description', 'perks']
    filter_horizontal = ['perks']
    formfield_overrides = {
        models.ForeignKey: {'widget': forms.Select(attrs={'style': 'width:180px'})},
    }
    model = SkillLevel
    extra = 2

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('perks')

    
@admin.register(Skill, RegularSkill, MentalSkill)
class SkillAdmin(admin.ModelAdmin):
    fields = [
        'name', 'weapon_type', 'tested_trait', 'image', 'group', 'types',
        'allowees',
    ]
    filter_horizontal = ['allowees', 'types']
    inlines = [RegularSkillLevelInline]
    list_display = ['id', 'name', 'tested_trait', 'image', 'group']
    list_editable = ['name', 'tested_trait', 'image', 'group']
    list_select_related = ['group']
    search_fields = ['name']
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        for field in [
            'group',
        ]:
            if db_field.name == field:
                formfield = formfield_with_cache(field, formfield, request)
        return formfield
    

class PowerSkillLevelInline(admin.StackedInline):
    fields = [
        (
            'skill', 'level', 'distance', 'radius', 'duration',
            'saving_throw_trait', 'saving_throw_malus', 'damage',
        ),
        'description',
    ]
    formfield_overrides = {
        models.ForeignKey: {'widget': forms.Select(attrs={'style': 'width:180px'})},
        models.TextField: {'widget': forms.Textarea(attrs={'rows': 30, 'cols': 80})},
    }
    model = PriestsSkillLevel
    extra = 0
    
    
@admin.register(PriestsSkill, SorcerersSkill, TheurgistsSkill)
class PowerSkillAdmin(SkillAdmin):
    fields = ['name', 'name_second', 'name_origin', 'types', 'allowees']
    inlines = [PowerSkillLevelInline]
    list_display = ['id', 'name', 'tested_trait']
    list_editable = ['name', 'tested_trait']


# -----------------------------------------------------------------------------

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


@admin.register(Synergy, RegularSynergy, MentalSynergy)
class SynergyAdmin(admin.ModelAdmin):
    filter_horizontal = ['skills']
    formfield_overrides = {
        models.CharField: {'widget': forms.Textarea(attrs={'rows': 3, 'cols': 10})},
        models.TextField: {'widget': forms.Textarea(attrs={'rows': 10, 'cols': 30})},
    }
    # inlines = [SynergyLevelInline]
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


# -----------------------------------------------------------------------------


@admin.register(SkillLevel, RegularSkillLevel, MentalSkillLevel)
class SkillLevelAdmin(admin.ModelAdmin):
    fields = ['skill', 'level', 'description', 'perks']
    filter_horizontal = ['perks']
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(attrs={'rows': 8, 'cols': 80})},
    }
    list_display = ['name', 'description']
    list_editable = ['description']
    list_filter = [SkillLevelFilter]
    list_select_related = ['skill']
    search_fields = ['skill__name', 'level', 'description']

    def name(self, obj):
        return f'{str(obj.skill.name)} [{obj.level}]'

    
@admin.register(PriestsSkillLevel, SorcerersSkillLevel, TheurgistsSkillLevel)
class PowerSkillLevelAdmin(admin.ModelAdmin):
    fields = [
        'skill', 'level', 'distance', 'radius', 'damage', 'saving_throw_trait',
        'saving_throw_malus', 'duration', 'description',
    ]

# -----------------------------------------------------------------------------


@admin.register(SynergyLevel, RegularSynergyLevel, MentalSynergyLevel)
class SynergyLevelAdmin(admin.ModelAdmin):
    filter_horizontal = ['perks', 'skill_levels']
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(attrs={'rows': 8, 'cols': 80})},
    }
    list_display = ['name', 'level', 'description']
    list_editable = ['level', 'description']
    list_filter = [SynergyLevelFilter]
    list_select_related = ['synergy']
    search_fields = ['level', 'description']

    def name(self, obj):
        return f'{str(obj.synergy.name)} [{obj.level}]'

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "skill_levels":
            kwargs["queryset"] = SkillLevel.objects.select_related('skill')
        return super().formfield_for_manytomany(db_field, request, **kwargs)


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
                types__kinds__name__in=["Powszechne", "Mentalne"]).distinct()
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related('profession')
        return qs


# -----------------------------------------------------------------------------


class SphragisAdminAdminForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['color'].help_text = """
            <a href="https://www.w3schools.com/colors/colors_picker.asp" target="_blank">
                https://www.w3schools.com/colors/colors_picker.asp
            </a>"""
        
    class Meta:
        model = Sphragis
        exclude = []
        widgets = {'color': forms.TextInput(attrs={'type': 'color'})}


@admin.register(Sphragis)
class SphragisAdmin(admin.ModelAdmin):
    form = SphragisAdminAdminForm
    list_display = ['id', 'name', 'name_genitive', 'color']
    list_editable = ['name', 'name_genitive', 'color']


# -----------------------------------------------------------------------------


@admin.register(DamageType)
class DamageTypeAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.CharField: {'widget': forms.TextInput(attrs={'size': 15})},
    }
    list_display = [
        '__str__', 'description', 'type', 'damage', 'special', '_weapon_types',
    ]
    list_editable = ['description', 'type', 'damage', 'special']
    list_filter = ['type', 'description']
    search_fields = ['description', 'damage', 'special']

    def _weapon_types(self, obj):
        weapon_types = " | ".join([wt.name for wt in obj.weapon_types.all()])
        return format_html(f'<span>{weapon_types}</span>')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.prefetch_related('weapon_types')
        return qs


@admin.register(WeaponType)
class WeaponTypeAdmin(admin.ModelAdmin):
    filter_horizontal = ['allowees', 'damage_types', 'comparables']
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(attrs={'rows': 5, 'cols': 100})},
        models.ForeignKey: {'widget': forms.Select(attrs={'style': 'width:180px'})},
    }
    list_display = [
        'name', 'description', 'size', 'trait', 'avg_price_value',
        'avg_price_currency', 'avg_weight',
    ]
    list_editable = [
        'description', 'size', 'trait', 'avg_price_value',
        'avg_price_currency', 'avg_weight',
    ]
    search_fields = ['name', 'description']


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
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        for field in [
            'picture_set',
        ]:
            if db_field.name == field:
                formfield = formfield_with_cache(field, formfield, request)
        return formfield

