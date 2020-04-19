from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.db import models
from django.db.models import Q
from django.forms import Textarea
from django.utils.translation import ugettext_lazy

from imaginarion.models import Picture
from knowledge.models import KnowledgePacket
from rules.models import Skill, SkillLevel, Synergy, SynergyLevel, CharacterClass, CharacterProfession, EliteClass, \
    EliteProfession, WeaponClass, WeaponType, PlateType, ShieldType
from users.models import Profile


class Form1(forms.ModelForm):
    allowed_profiles = forms.ModelMultipleChoiceField(
        queryset=Profile.objects.exclude(Q(status='dead_player')
                                         | Q(status='dead_npc')
                                         | Q(status='gm')
                                         | Q(status='living_npc')),
        required=False,
        widget=FilteredSelectMultiple('Allowed profiles', False),
    )


class Form2(forms.ModelForm):
    allowed_profiles = forms.ModelMultipleChoiceField(
        queryset=Profile.objects.exclude(Q(status='dead_player')
                                         | Q(status='dead_npc')
                                         | Q(status='gm')
                                         | Q(status='living_npc')),
        required=False,
        widget=FilteredSelectMultiple('Allowed profiles', False),
    )
    pictures = forms.ModelMultipleChoiceField(
        queryset=Picture.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('Pictures', False),
    )


class Form3(forms.ModelForm):
    allowed_profiles = forms.ModelMultipleChoiceField(
        queryset=Profile.objects.exclude(Q(status='dead_player')
                                         | Q(status='dead_npc')
                                         | Q(status='gm')
                                         | Q(status='living_npc')),
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


class CharacterProfessionInline(admin.TabularInline):
    model = CharacterProfession
    extra = 2

    fields = ['name', 'description', 'start_perks', 'allowed_profiles']
    form = Form1
    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 1, 'cols': 10})},
        models.TextField: {'widget': Textarea(attrs={'rows': 15, 'cols': 40})},
    }


class CharacterProfessionAdmin(admin.ModelAdmin):
    form = Form1
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

    form = Form1
    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 1, 'cols': 10})},
        models.TextField: {'widget': Textarea(attrs={'rows': 15, 'cols': 40})},
    }


class EliteProfessionAdmin(admin.ModelAdmin):
    form = Form1
    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 1, 'cols': 10})},
        models.TextField: {'widget': Textarea(attrs={'rows': 10, 'cols': 60})},
    }
    list_display = ['name', 'elite_class', 'description', 'start_perks']
    list_editable = ['description', 'start_perks']
    search_fields = ['name', 'description', 'start_perks']


class EliteClassAdmin(admin.ModelAdmin):
    form = Form1
    inlines = [EliteProfessionInline]
    list_display = ['name', 'description']
    list_editable = ['description']
    search_fields = ['name', 'description']


class WeaponTypeInline(admin.TabularInline):
    model = WeaponType
    extra = 2

    form = Form2
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
    form = Form2
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 2, 'cols': 100})},
    }
    list_display = ['name', 'description']
    list_editable = ['description']
    search_fields = ['name', 'description']


class PlateTypeAdmin(admin.ModelAdmin):
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
admin.site.register(SkillLevel, SkillLevelAdmin)
admin.site.register(Synergy, SynergyAdmin)
admin.site.register(SynergyLevel, SynergyLevelAdmin)
admin.site.register(CharacterClass, CharacterClassAdmin)
admin.site.register(CharacterProfession, CharacterProfessionAdmin)
admin.site.register(EliteClass, EliteClassAdmin)
admin.site.register(EliteProfession, EliteProfessionAdmin)
admin.site.register(WeaponClass, WeaponClassAdmin)
admin.site.register(WeaponType, WeaponTypeAdmin)
admin.site.register(PlateType, PlateTypeAdmin)
admin.site.register(ShieldType, ShieldTypeAdmin)
