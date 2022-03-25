from django import forms
from django.contrib import admin
from django.db import models
from django.utils.html import format_html

from prosoponomikon.models import Character, NPCCharacter, PlayerCharacter, \
    FirstName, NameGroup, FamilyName, AffixGroup, \
    AuxiliaryNameGroup, FamilyNameGroup
from rpg_project.utils import formfield_for_dbfield_cached, formfield_with_cache


@admin.register(FirstName)
class FirstNameAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(attrs={'rows': 3, 'cols': 40})},
        models.CharField: {'widget': forms.TextInput(attrs={'size': 20})},
    }
    list_display = [
        'id', 'form', 'form_2', 'is_ancient', 'info', 'affix_group',
        'auxiliary_group']
    list_editable = [
        'form', 'form_2', 'is_ancient', 'info', 'affix_group',
        'auxiliary_group']
    list_filter = ['auxiliary_group', 'is_ancient']
    ordering = ['form']
    search_fields = ['form', 'form_2']

    def formfield_for_dbfield(self, db_field, **kwargs):
        fields = [
            'affix_group',
            'auxiliary_group',
        ]
        return formfield_for_dbfield_cached(self, db_field, fields, **kwargs)
    
    
class FirstNameInline(admin.TabularInline):
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(attrs={'rows': 3, 'cols': 50})},
    }
    model = FirstName
    extra = 10
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        fields = [
            'auxiliary_group',
        ]
        return formfield_for_dbfield_cached(self, db_field, fields, **kwargs)


# -----------------------------------------------------------------------------


@admin.register(FamilyName)
class FamilyNameAdmin(admin.ModelAdmin):
    filter_horizontal = ['locations']
    list_display = ['id', 'group', 'form', 'info', 'locs']
    list_editable = ['group', 'form', 'info']
    ordering = ['group', 'form']

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        form_field = super().formfield_for_manytomany(db_field, request, **kwargs)
        if db_field.name == 'locations':
            form_field.widget.attrs = {'style': 'height:400px'}
        return form_field

    # def formfield_for_dbfield(self, db_field, **kwargs):
    #     fields = [
    #         'group',
    #     ]
    #     return formfield_for_dbfield_cached(self, db_field, fields, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        fields = [
            'group',
        ]
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        for field in fields:
            if db_field.name == field:
                formfield = formfield_with_cache(field, formfield, request)
        return formfield
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.prefetch_related('locations', 'group')
        return qs

    def locs(self, obj):
        return " | ".join([loc.name for loc in obj.locations.all()])


# -----------------------------------------------------------------------------


@admin.register(NameGroup)
class NameGroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'type', 'description']
    list_editable = ['title', 'type', 'description']


@admin.register(FamilyNameGroup)
class FamilyNameGroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'description']
    list_editable = ['title', 'description']


# -----------------------------------------------------------------------------


@admin.register(AffixGroup)
class AffixGroupAdmin(admin.ModelAdmin):
    inlines = [FirstNameInline]
    list_display = ['id', 'affix', 'type', 'name_group']
    list_editable = ['affix', 'type', 'name_group']
    list_filter = ['type']

    def formfield_for_dbfield(self, db_field, **kwargs):
        fields = [
            'name_group',
        ]
        return formfield_for_dbfield_cached(self, db_field, fields, **kwargs)
    

@admin.register(AuxiliaryNameGroup)
class AuxiliaryNameGroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'color', 'location', 'social_info']
    list_editable = ['color', 'location', 'social_info']
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        fields = [
            'location',
        ]
        return formfield_for_dbfield_cached(self, db_field, fields, **kwargs)
   

@admin.register(Character, PlayerCharacter, NPCCharacter)
class CharacterAdmin(admin.ModelAdmin):
    filter_horizontal = [
        'frequented_locations', 'biography_packets', 'dialogue_packets',
        'witnesses', 'known_indirectly', 'professions']
    list_display = [
        'get_img', 'first_name', 'family_name', 'cognomen', 'description']
    list_editable = ['first_name', 'family_name', 'cognomen', 'description']
    search_fields = [
        'first_name__form', 'family_name__form', 'cognomen', 'description']

    def formfield_for_dbfield(self, db_field, **kwargs):
        fields = [
            'first_name',
            'family_name',
        ]
        return formfield_for_dbfield_cached(self, db_field, fields, **kwargs)
    
    def get_img(self, obj):
        if obj.profile.image:
            return format_html(
                f'<img src="{obj.profile.image.url}" width="70" height="70">'
            )
        default_img = "media/profile_pics/profile_default.jpg"
        return format_html(f'<img src={default_img} width="70" height="70">')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related('profile', 'first_name', 'family_name')
        return qs
