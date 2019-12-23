from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.db.models import Q
from django.db import models
from django.forms import Textarea

from imaginarion.models import Picture
from rules.models import Skill, SkillLevel, Synergy, CharacterClass, CharacterProfession, EliteClass, EliteProfession, \
    WeaponClass, WeaponType, PlateType, ShieldType
from users.models import Profile


class ForAllowedProfilesForm(forms.ModelForm):
    allowed_profiles = forms.ModelMultipleChoiceField(queryset=Profile.objects
                                                      .exclude(Q(character_status='dead_player') |
                                                               Q(character_status='dead_npc') |
                                                               Q(character_status='gm') |
                                                               Q(character_status='living_npc')),
                                                      widget=FilteredSelectMultiple('Allowed profiles', False),
                                                      required=False)


class ForAllowedProfilesAndPicturesForm(forms.ModelForm):
    allowed_profiles = forms.ModelMultipleChoiceField(queryset=Profile.objects
                                                      .exclude(Q(character_status='dead_player') |
                                                               Q(character_status='dead_npc') |
                                                               Q(character_status='gm') |
                                                               Q(character_status='living_npc')),
                                                      widget=FilteredSelectMultiple('Allowed profiles', False),
                                                      required=False)
    pictures = forms.ModelMultipleChoiceField(queryset=Picture.objects.all(),
                                              widget=FilteredSelectMultiple('Pictures', False),
                                              required=False)


class SkillLevelAdmin(admin.ModelAdmin):
    pass
    # list_display = ['name']
    # search_fields = ['name']
    #
    # def name(self, obj):
    #     return f'{obj.skill} {obj.level}'


class SkillLevelInline(admin.TabularInline):
    model = SkillLevel
    extra = 4


class SkillAdmin(admin.ModelAdmin):
    form = ForAllowedProfilesForm
    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 2, 'cols': 10})},
        models.TextField: {'widget': Textarea(attrs={'rows': 10, 'cols': 30})},
    }
    inlines = [SkillLevelInline]
    list_display = ['id', 'name', 'tested_trait', 'description', 'lvl_0', 'lvl_1', 'lvl_2', 'lvl_3', 'image']
    list_editable = ['name', 'description', 'tested_trait', 'lvl_0', 'lvl_1', 'lvl_2', 'lvl_3', 'image']
    search_fields = ['name', 'description', 'lvl_0', 'lvl_1', 'lvl_2', 'lvl_3']


class SynergyAdmin(admin.ModelAdmin):
    form = ForAllowedProfilesForm
    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 3, 'cols': 10})},
        models.TextField: {'widget': Textarea(attrs={'rows': 10, 'cols': 30})},
    }
    list_display = ['id', 'name', 'lvl_1', 'lvl_2', 'lvl_3']
    list_editable = ['name', 'lvl_1', 'lvl_2', 'lvl_3']
    search_fields = ['name', 'lvl_1', 'lvl_2', 'lvl_3']


class CharacterProfessionInline(admin.TabularInline):
    model = CharacterProfession
    extra = 2

    fields = ['name', 'description', 'start_perks', 'allowed_profiles']
    form = ForAllowedProfilesForm
    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 1, 'cols': 10})},
        models.TextField: {'widget': Textarea(attrs={'rows': 15, 'cols': 40})},
    }


class CharacterProfessionAdmin(admin.ModelAdmin):
    form = ForAllowedProfilesForm
    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 1, 'cols': 10})},
        models.TextField: {'widget': Textarea(attrs={'rows': 10, 'cols': 60})},
    }
    list_display = ['name', 'character_class', 'description', 'start_perks']
    list_editable = ['description', 'start_perks']
    search_fields = ['name', 'description', 'start_perks']


class CharacterClassAdmin(admin.ModelAdmin):
    inlines = [CharacterProfessionInline]
    list_display = ['name', 'description']
    list_editable = ['description']
    search_fields = ['name', 'description']


class EliteProfessionInline(admin.TabularInline):
    model = EliteProfession
    extra = 2

    form = ForAllowedProfilesForm
    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 1, 'cols': 10})},
        models.TextField: {'widget': Textarea(attrs={'rows': 15, 'cols': 40})},
    }


class EliteProfessionAdmin(admin.ModelAdmin):
    form = ForAllowedProfilesForm
    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 1, 'cols': 10})},
        models.TextField: {'widget': Textarea(attrs={'rows': 10, 'cols': 60})},
    }
    list_display = ['name', 'elite_class', 'description', 'start_perks']
    list_editable = ['description', 'start_perks']
    search_fields = ['name', 'description', 'start_perks']


class EliteClassAdmin(admin.ModelAdmin):
    form = ForAllowedProfilesForm
    inlines = [EliteProfessionInline]
    list_display = ['name', 'description']
    list_editable = ['description']
    search_fields = ['name', 'description']


class WeaponTypeInline(admin.TabularInline):
    model = WeaponType
    extra = 2

    form = ForAllowedProfilesAndPicturesForm
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 25})},
        models.CharField: {'widget': Textarea(attrs={'rows': 1, 'cols': 5})},
    }


class WeaponClassAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 2, 'cols': 100})},
    }
    inlines = [WeaponTypeInline, ]
    list_display = ['name', 'description']
    list_editable = ['description']
    search_fields = ['name', 'description']


class WeaponTypeAdmin(admin.ModelAdmin):
    form = ForAllowedProfilesAndPicturesForm
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 2, 'cols': 100})},
    }
    list_display = ['name', 'description']
    list_editable = ['description']
    search_fields = ['name', 'description']


class PlateTypeAdmin(admin.ModelAdmin):
    form = ForAllowedProfilesAndPicturesForm
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 2, 'cols': 100})},
    }
    list_display = ['name', 'description']
    list_editable = ['description']
    search_fields = ['name', 'description']


class ShieldTypeAdmin(admin.ModelAdmin):
    form = ForAllowedProfilesForm
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 2, 'cols': 100})},
    }
    list_display = ['name', 'description']
    list_editable = ['description']
    search_fields = ['name', 'description']


admin.site.register(Skill, SkillAdmin)
admin.site.register(SkillLevel, SkillLevelAdmin)
admin.site.register(Synergy, SynergyAdmin)
admin.site.register(CharacterClass, CharacterClassAdmin)
admin.site.register(CharacterProfession, CharacterProfessionAdmin)
admin.site.register(EliteClass, EliteClassAdmin)
admin.site.register(EliteProfession, EliteProfessionAdmin)
admin.site.register(WeaponClass, WeaponClassAdmin)
admin.site.register(WeaponType, WeaponTypeAdmin)
admin.site.register(PlateType, PlateTypeAdmin)
admin.site.register(ShieldType, ShieldTypeAdmin)
