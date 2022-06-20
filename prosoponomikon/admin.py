from django import forms
from django.contrib import admin
from django.db import models
from django.utils.html import format_html

from prosoponomikon.models import Character, NPCCharacter, PlayerCharacter, \
    FirstName, FirstNameGroup, FamilyName, AffixGroup, \
    AuxiliaryNameGroup, FamilyNameGroup, Acquaintanceship
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
        'id', 'form', 'form_2', 'is_ancient', 'info', 'affix_group',
        'auxiliary_group'
    ]
    list_editable = [
        'form', 'form_2', 'is_ancient', 'info', 'affix_group',
        'auxiliary_group'
    ]
    list_filter = ['auxiliary_group', 'is_ancient']
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


@admin.register(AuxiliaryNameGroup)
class AuxiliaryNameGroupAdmin(admin.ModelAdmin):
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
    ]
    list_display = [
        'id', 'knowing_character', 'known_character', 'is_direct',
        'knows_if_dead',
    ]
    list_editable = [
        'knowing_character', 'known_character', 'is_direct', 'knows_if_dead',
    ]
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


class AcquaintanceshipInline(admin.TabularInline):
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


# -----------------------------------------------------------------------------


@admin.register(Character, PlayerCharacter, NPCCharacter)
class CharacterAdmin(admin.ModelAdmin):
    fields = [
        'profile', 'first_name', 'family_name', 'cognomen', 'fullname',
        'description', 'frequented_locations', 'biography_packets',
        'dialogue_packets', 'subprofessions', 'participants', 'informees',
    ]
    filter_horizontal = [
        'frequented_locations', 'biography_packets', 'dialogue_packets',
        'participants', 'informees', 'subprofessions', 'acquaintances',
    ]
    inlines = [AcquaintanceshipInline]
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
