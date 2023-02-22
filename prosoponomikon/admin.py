from django import forms
from django.contrib import admin
from django.db import models
from django.utils.html import format_html

from prosoponomikon.models import Acquaintanceship, Acquisition, \
    Character, NPCCharacter, PlayerCharacter, \
    CharacterAcquaintanceships, CharacterAcquisitions, \
    FirstName, FirstNameGroup, FamilyName, \
    AffixGroup, AuxiliaryNameGroup, FamilyNameGroup
from rpg_project.utils import formfield_with_cache


# -----------------------------------------------------------------------------


@admin.register(FirstNameGroup)
class FirstNameGroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'type', 'description']
    list_editable = ['title', 'type', 'description']


@admin.register(FamilyName)
class FamilyNameAdmin(admin.ModelAdmin):
    fields = ['form', 'group', 'info', 'locations']
    filter_horizontal = ['locations']
    list_display = ['id', 'group', 'form', 'info', 'locs']
    list_editable = ['group', 'form', 'info']
    ordering = ['group', 'form']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        for field in [
            'group',
        ]:
            if db_field.name == field:
                formfield = formfield_with_cache(field, formfield, request)
        return formfield

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        form_field = super().formfield_for_manytomany(db_field, request, **kwargs)
        if db_field.name in [
            'locations',
        ]:
            form_field.widget.attrs = {'style': 'height:400px'}
        return form_field

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.prefetch_related('locations', 'group')
        return qs

    def locs(self, obj):
        return " | ".join([loc.name for loc in obj.locations.all()])


# -----------------------------------------------------------------------------


@admin.register(FamilyNameGroup)
class FamilyNameGroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'description']
    list_editable = ['title', 'description']


@admin.register(FirstName)
class FirstNameAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(attrs={'rows': 3, 'cols': 40})},
        models.CharField: {'widget': forms.TextInput(attrs={'size': 20})},
        models.ForeignKey: {'widget': forms.Select(attrs={'style': 'width:180px'})},
    }
    list_display = [
        'id', 'form', 'form_2', 'info', 'affix_group', 'auxiliary_group'
    ]
    list_editable = [
        'form', 'form_2', 'info', 'affix_group', 'auxiliary_group'
    ]
    list_filter = ['auxiliary_group']
    ordering = ['form']
    search_fields = ['form', 'form_2']
    list_select_related = True

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        for field in [
            'affix_group',
            'auxiliary_group',
        ]:
            if db_field.name == field:
                formfield = formfield_with_cache(field, formfield, request)
        return formfield


class FirstNameInline(admin.TabularInline):
    model = FirstName
    extra = 10
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(attrs={'rows': 3, 'cols': 50})},
    }

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        for field in [
            'auxiliary_group',
        ]:
            if db_field.name == field:
                formfield = formfield_with_cache(field, formfield, request)
        return formfield


@admin.register(AffixGroup)
class AffixGroupAdmin(admin.ModelAdmin):
    inlines = [FirstNameInline]
    list_display = ['id', 'affix', 'type', 'name_group']
    list_editable = ['affix', 'type', 'name_group']
    list_filter = ['type']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        for field in [
            'name_group',
        ]:
            if db_field.name == field:
                formfield = formfield_with_cache(field, formfield, request)
        return formfield


class AuxiliaryNameGroupAdminForm(forms.ModelForm):

    class Meta:
        model = AuxiliaryNameGroup
        exclude = []
        widgets = {'color': forms.TextInput(attrs={'type': 'color'})}


@admin.register(AuxiliaryNameGroup)
class AuxiliaryNameGroupAdmin(admin.ModelAdmin):
    form = AuxiliaryNameGroupAdminForm
    formfield_overrides = {
        models.CharField: {'widget': forms.TextInput(attrs={'type': 'color'})},
    }

    list_display = ['id', 'color', 'location', 'social_info']
    list_editable = ['color', 'location', 'social_info']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        for field in [
            'location',
        ]:
            if db_field.name == field:
                formfield = formfield_with_cache(field, formfield, request)
        return formfield


# -----------------------------------------------------------------------------


@admin.register(Acquaintanceship)
class AcquaintanceshipAdmin(admin.ModelAdmin):
    fields = [
        'knowing_character', 'known_character', 'is_direct', 'knows_if_dead',
        'knows_as_name', 'knows_as_description', 'knows_as_image',
    ]
    list_display = [
        'id', 'knowing_character', 'known_character', 'is_direct', 'knows_if_dead',
        'knows_as_name', 'knows_as_description', 'knows_as_image',
    ]
    list_editable = [
        'knowing_character', 'known_character', 'is_direct', 'knows_if_dead',
        'knows_as_name', 'knows_as_description', 'knows_as_image',
    ]
    list_filter = ['known_character__profile__is_alive']
    list_select_related = ['knowing_character', 'known_character']
    search_fields = [
        'knowing_character__fullname', 'known_character__fullname'
    ]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        for field in [
            'knowing_character',
            'known_character',
        ]:
            if db_field.name == field:
                formfield = formfield_with_cache(field, formfield, request)
        return formfield


class AcquaintanceshipActiveInline(admin.TabularInline):
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(attrs={'rows': 3, 'cols': 40})},
    }
    model = Character.acquaintances.through
    fk_name = 'knowing_character'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('known_character', 'knowing_character')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        for field in [
            'known_character',
            'knowing_character',
        ]:
            if db_field.name == field:
                formfield = formfield_with_cache(field, formfield, request)
        return formfield


class AcquaintanceshipPassiveInline(AcquaintanceshipActiveInline):
    model = Character.acquaintances.through
    fk_name = 'known_character'


# -----------------------------------------------------------------------------


class AcquisitionAdminForm(forms.ModelForm):
    """Custom form for query optimization."""

    class Meta:
        model = Acquisition
        exclude = []

    def __init__(self, *args, **kwargs):
        from rules.models import SkillLevel
        super().__init__(*args, **kwargs)
        self.fields['skill_level'].queryset = SkillLevel.objects.select_related('skill')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        for field in [
            'skill_level',
        ]:
            if db_field.name == field:
                formfield = formfield_with_cache(field, formfield, request)
        return formfield

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related(
            'skill_level__skill',
        )
        return qs


@admin.register(Acquisition)
class AcquisitionAdmin(admin.ModelAdmin):
    fields = ['character', 'skill_level', 'weapon_type', 'sphragis']
    form = AcquisitionAdminForm
    list_display = [
        'get_img', 'character', 'skill_level', 'weapon_type', 'sphragis'
    ]
    list_filter = ['sphragis', 'character', 'skill_level__skill', 'weapon_type']
    search_fields = ['skill_level', 'character', 'weapon_type', 'sphragis']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related(
            'skill_level__skill',
            'character__first_name',
            'character__family_name',
            'character__profile',
            'weapon_type',
            'sphragis',
        )
        return qs

    def get_img(self, obj):
        if obj.character.profile.image:
            return format_html(
                f'<img src="{obj.character.profile.image.url}" width="70" height="70">')
        default_img = "media/profile_pics/profile_default.jpg"
        return format_html(f'<img src={default_img} width="70" height="70">')


class AcquisitionInline(admin.TabularInline):
    model = Character.skill_levels.through

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        for field in [
            'sphragis',
            'weapon_type',
        ]:
            if db_field.name == field:
                formfield = formfield_with_cache(field, formfield, request)
        return formfield

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        formset.form.base_fields["skill_level"].queryset = \
            formset.form.base_fields["skill_level"].queryset.select_related("skill")
        return formset

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related(
            'character', 'skill_level__skill', 'sphragis', 'weapon_type')


# -----------------------------------------------------------------------------


@admin.register(Character, PlayerCharacter, NPCCharacter)
class CharacterAdmin(admin.ModelAdmin):
    fields = [
        'profile',
        ('first_name', 'family_name', 'cognomen', 'fullname'),
        ('strength', 'dexterity', 'endurance', 'experience'),
        'description', 'frequented_locations', 'biography_packets',
        'dialogue_packets', 'subprofessions',
    ]
    filter_horizontal = [
        'frequented_locations', 'biography_packets', 'dialogue_packets',
        'subprofessions', 'acquaintances',
    ]
    list_display = [
        'get_img', 'first_name', 'family_name', 'cognomen', 'description'
    ]
    list_editable = ['first_name', 'family_name', 'cognomen', 'description']
    readonly_fields = ['fullname']
    search_fields = [
        'first_name__form', 'first_name__form_2', 'family_name__form',
        'cognomen', 'description'
    ]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        for field in [
            'first_name',
            'family_name',
        ]:
            if db_field.name == field:
                formfield = formfield_with_cache(field, formfield, request)
        return formfield

    def get_img(self, obj):
        if obj.profile.image:
            img = f'<img src="{obj.profile.image.url}" width="70" height="70">'
        else:
            img = f'<img src="media/profile_pics/profile_default.jpg" width="70" height="70">'
        return format_html(img)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related('profile', 'first_name', 'family_name')
        return qs


@admin.register(CharacterAcquaintanceships)
class CharacterAcquaintanceshipsAdmin(CharacterAdmin):
    fields = ['profile', 'fullname']
    inlines = [AcquaintanceshipActiveInline, AcquaintanceshipPassiveInline]


@admin.register(CharacterAcquisitions)
class CharacterAcquisitionsAdmin(CharacterAdmin):
    fields = [
        'fullname',
        ('strength', 'dexterity', 'endurance', 'experience'),
    ]
    inlines = [AcquisitionInline]
