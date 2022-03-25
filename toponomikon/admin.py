from django import forms
from django.contrib import admin
from django.db import models

from rpg_project.utils import formfield_for_dbfield_cached, formfield_with_cache
from toponomikon.models import LocationType, Location, PrimaryLocation, SecondaryLocation


# -----------------------------------------------------------------------------


@admin.register(LocationType)
class LocationTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'order_no', 'name', 'name_plural', 'default_img']
    list_editable = ['order_no', 'name', 'name_plural', 'default_img']
    list_select_related = ['default_img']

    def formfield_for_dbfield(self, db_field, **kwargs):
        fields = [
            'default_img',
        ]
        return formfield_for_dbfield_cached(self, db_field, fields, **kwargs)

# -----------------------------------------------------------------------------


@admin.register(Location, SecondaryLocation, PrimaryLocation)
class LocationAdmin(admin.ModelAdmin):
    filter_horizontal = [
        'witnesses', 'known_indirectly', 'knowledge_packets',
        'map_packets', 'picture_sets']
    formfield_overrides = {
        models.CharField: {'widget': forms.TextInput(attrs={'size': 15})},
        models.ForeignKey: {'widget': forms.Select(attrs={'style': 'width:150px'})},
        models.TextField: {'widget': forms.Textarea(attrs={'rows': 12, 'cols': 40})},
    }
    list_display = [
        'id', 'name', 'location_type', 'in_location', 'main_image',
        'description', 'audio_set']
    list_editable = [
        'name', 'location_type', 'in_location', 'main_image',
        'description', 'audio_set']
    list_filter = ['location_type__name']
    list_select_related = [
        'location_type__default_img', 'in_location', 'main_image', 'audio_set']
    search_fields = ['name', 'description']
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        fields = [
            'location_type',
            'in_location',
            'main_image',
            'audio_set',
        ]
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        for field in fields:
            if db_field.name == field:
                formfield = formfield_with_cache(field, formfield, request)
        return formfield
