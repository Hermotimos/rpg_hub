from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.db import models
from django.db.models import Q
from django.forms import Textarea, TextInput, Select

from imaginarion.models import Picture
from knowledge.models import KnowledgePacket
from toponomikon.models import LocationType, Location, PrimaryLocation, \
    SecondaryLocation
from users.models import Profile


class ToponomikonForm(forms.ModelForm):
    known_directly = forms.ModelMultipleChoiceField(
        queryset=Profile.objects.exclude(Q(status='dead_player')
                                         | Q(status='dead_npc')
                                         | Q(status='gm')
                                         | Q(status='living_npc')),
        widget=FilteredSelectMultiple('Known directly', False),
        required=False
    )
    known_indirectly = forms.ModelMultipleChoiceField(
        queryset=Profile.objects.exclude(Q(status='dead_player')
                                         | Q(status='dead_npc')
                                         | Q(status='gm')
                                         | Q(status='living_npc')),
        widget=FilteredSelectMultiple('Known indirectly', False),
        required=False
    )
    knowledge_packets = forms.ModelMultipleChoiceField(
        queryset=KnowledgePacket.objects.all(),
        widget=FilteredSelectMultiple('Knowledge packets', False),
        required=False
    )
    pictures = forms.ModelMultipleChoiceField(
        queryset=Picture.objects.all(),
        widget=FilteredSelectMultiple('Pictures', False),
        required=False
    )


class LocationInline(admin.TabularInline):
    model = Location
    extra = 0
    form = ToponomikonForm
    fields = ['name', 'location_type', 'main_image', 'description']
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': 20})},
        models.ForeignKey: {'widget': Select(attrs={'style': 'width:220px'})},
        models.TextField: {'widget': Textarea(attrs={'rows': 15, 'cols': 100})},
    }

    def formfield_for_dbfield(self, db_field, **kwargs):
        # https://blog.ionelmc.ro/2012/01/19/tweaks-for-making-django-admin-faster/
        # Reduces greatly queries in main view, doubles in detail view
        # The trade-off is still very good
        request = kwargs['request']
        formfield = super().formfield_for_dbfield(db_field, **kwargs)
        
        if db_field.name == 'location_type':
            choices = getattr(request, '_location_type_choices_cache', None)
            if choices is None:
                request._main_location_type_cache = choices = list(
                    formfield.choices)
            formfield.choices = choices
           
        if db_field.name == 'in_location':
            choices = getattr(request, '_in_location_choices_cache', None)
            if choices is None:
                request._main_in_location_cache = choices = list(
                    formfield.choices)
            formfield.choices = choices
           
        if db_field.name == 'main_image':
            choices = getattr(request, '_main_image_choices_cache', None)
            if choices is None:
                request._main_main_image_cache = choices = list(
                    formfield.choices)
            formfield.choices = choices
            
        return formfield
    

class LocationAdmin(admin.ModelAdmin):
    form = ToponomikonForm
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': 15})},
        models.ForeignKey: {'widget': Select(attrs={'style': 'width:200px'})},
        models.TextField: {'widget': Textarea(attrs={'rows': 10, 'cols': 55})},
    }
    inlines = [LocationInline]
    list_display = ['id', 'name', 'location_type', 'in_location', 'main_image', 'description']
    list_editable = ['name', 'location_type', 'in_location', 'main_image', 'description']
    list_filter = ['location_type__name']
    list_select_related = ['location_type__default_img', 'in_location', 'main_image']
    search_fields = ['name', 'description']

    def formfield_for_dbfield(self, db_field, **kwargs):
        # https://blog.ionelmc.ro/2012/01/19/tweaks-for-making-django-admin-faster/
        # Reduces greatly queries in main view, doubles in detail view
        # The trade-off is still very good
        request = kwargs['request']
        formfield = super().formfield_for_dbfield(db_field, **kwargs)
    
        if db_field.name == 'location_type':
            choices = getattr(request, '_location_type_choices_cache', None)
            if choices is None:
                request._main_location_type_cache = choices = list(
                    formfield.choices)
            formfield.choices = choices
            
        if db_field.name == 'in_location':
            choices = getattr(request, '_in_location_choices_cache', None)
            if choices is None:
                request._main_in_location_cache = choices = list(
                    formfield.choices)
            formfield.choices = choices
    
        if db_field.name == 'main_image':
            choices = getattr(request, '_main_image_choices_cache', None)
            if choices is None:
                request._main_main_image_cache = choices = list(
                    formfield.choices)
            formfield.choices = choices
    
        return formfield
    

class PrimaryLocationAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.ForeignKey: {'widget': Select(attrs={'style': 'width:300px'})},
    }
    inlines = [LocationInline]
    list_display = ['id', 'name', 'main_image', 'description']
    list_editable = ['name', 'main_image', 'description']
    list_select_related = ['main_image']
    search_fields = ['name', 'description']
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        # https://blog.ionelmc.ro/2012/01/19/tweaks-for-making-django-admin-faster/
        # Reduces greatly queries in main view, doubles in detail view
        # The trade-off is still very good
        request = kwargs['request']
        formfield = super().formfield_for_dbfield(db_field, **kwargs)

        if db_field.name == 'main_image':
            choices = getattr(request, '_main_image_choices_cache', None)
            if choices is None:
                request._main_main_image_cache = choices = list(
                    formfield.choices)
            formfield.choices = choices

        return formfield
    
    
class SecondaryLocationAdmin(LocationAdmin):
    pass

#
# class TertiaryLocationAdmin(LocationAdmin):
#     pass
    
    
class LocationTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'order_no', 'name', 'name_plural', 'default_img']
    list_editable = ['order_no', 'name', 'name_plural', 'default_img']
    list_select_related = ['default_img']

    def formfield_for_dbfield(self, db_field, **kwargs):
        # https://blog.ionelmc.ro/2012/01/19/tweaks-for-making-django-admin-faster/
        request = kwargs['request']
        formfield = super().formfield_for_dbfield(db_field, **kwargs)

        if db_field.name == 'default_img':
            choices = getattr(request, '_default_img_choices_cache', None)
            if choices is None:
                request._default_img_choices_cache = choices = list(
                    formfield.choices)
            formfield.choices = choices

        return formfield


admin.site.register(LocationType, LocationTypeAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(PrimaryLocation, PrimaryLocationAdmin)
admin.site.register(SecondaryLocation, SecondaryLocationAdmin)
# admin.site.register(TertiaryLocation, TertiaryLocationAdmin)
