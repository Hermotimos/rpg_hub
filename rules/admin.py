from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.db import models
from django.forms import Textarea
from django.utils.translation import ugettext_lazy

from imaginarion.models import PictureSet
from knowledge.models import KnowledgePacket
from rules.models import Skill, SkillLevel, Synergy, SynergyLevel, \
    Profession, Klass, EliteProfession, BooksSkill, TheologySkill, \
    EliteKlass, WeaponType, Weapon, Plate, Shield
from users.models import Profile


class Form1(forms.ModelForm):
    allowed_profiles = forms.ModelMultipleChoiceField(
        queryset=Profile.players.filter(is_alive=True),
        required=False,
        widget=FilteredSelectMultiple('Allowed profiles', False),
    )


class Form2(forms.ModelForm):
    allowed_profiles = forms.ModelMultipleChoiceField(
        queryset=Profile.players.filter(is_alive=True),
        required=False,
        widget=FilteredSelectMultiple('Allowed profiles', False),
    )
    picture_sets = forms.ModelMultipleChoiceField(
        queryset=PictureSet.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('Picture Sets', False),
    )


class Form3(forms.ModelForm):
    allowed_profiles = forms.ModelMultipleChoiceField(
        queryset=Profile.players.filter(is_alive=True),
        required=False,
        widget=FilteredSelectMultiple('Allowed profiles', False)
    )
    skills = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('Skills', False)
    )


class Form4(forms.ModelForm):
    knowledge_packets = forms.ModelMultipleChoiceField(
        queryset=KnowledgePacket.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('Knowledge packets', False)
    )


class SkillLevelFilter(admin.SimpleListFilter):
    title = ugettext_lazy('skill__name')
    parameter_name = 'skill__name'

    def lookups(self, request, model_admin):
        qs = model_admin.get_queryset(request)
        qs.distinct()
        list_with_duplicates = [(i, i) for i in qs.values_list('skill__name', flat=True).distinct()]
        list_without_duplicates = list(dict.fromkeys(list_with_duplicates))
        return list_without_duplicates

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(skill__name__exact=self.value())


class SynergyLevelFilter(admin.SimpleListFilter):
    title = ugettext_lazy('synergy__name')
    parameter_name = 'synergy__name'

    def lookups(self, request, model_admin):
        qs = model_admin.get_queryset(request)
        qs.distinct()
        list_with_duplicates = [(i, i) for i in qs.values_list('synergy__name', flat=True).distinct()]
        list_without_duplicates = list(dict.fromkeys(list_with_duplicates))
        return list_without_duplicates

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(synergy__name__exact=self.value())


class SkillLevelAdmin(admin.ModelAdmin):
    form = Form4
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


class SkillLevelInline(admin.TabularInline):
    model = SkillLevel
    extra = 1


class SkillAdmin(admin.ModelAdmin):
    form = Form1
    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 2, 'cols': 10})},
        models.TextField: {'widget': Textarea(attrs={'rows': 10, 'cols': 30})},
    }
    inlines = [SkillLevelInline]
    list_display = ['id', 'name', 'tested_trait', 'image']
    list_editable = ['name', 'tested_trait', 'image']
    search_fields = ['name']


class SynergyLevelAdmin(admin.ModelAdmin):
    form = Form4
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


class SynergyLevelInline(admin.TabularInline):
    model = SynergyLevel
    extra = 1


class SynergyAdmin(admin.ModelAdmin):
    form = Form3
    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 3, 'cols': 10})},
        models.TextField: {'widget': Textarea(attrs={'rows': 10, 'cols': 30})},
    }
    inlines = [SynergyLevelInline]
    list_display = ['id', 'name']
    list_editable = ['name']
    search_fields = ['name']


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


class WeaponTypeInline(admin.TabularInline):
    model = Weapon
    extra = 2

    form = Form2
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 25})},
        models.CharField: {'widget': Textarea(attrs={'rows': 1, 'cols': 5})},
    }


class WeaponTypeAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 2, 'cols': 100})},
    }
    inlines = [WeaponTypeInline, ]
    list_display = ['name', 'description']
    list_editable = ['description']
    search_fields = ['name', 'description']


class WeaponAdmin(admin.ModelAdmin):
    form = Form2
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 2, 'cols': 100})},
    }
    list_display = ['name', 'description']
    list_editable = ['description']
    list_filter = ['weapon_type']
    search_fields = ['name', 'description']


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
