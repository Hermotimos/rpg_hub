from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.db import models
from django.db.models import Q
from django.forms import Textarea

from toponomikon.models import GeneralLocation, SpecificLocation, LocationType
from imaginarion.models import Picture
from knowledge.models import KnowledgePacket
from users.models import Profile


class ToponomikonKnownForm(forms.ModelForm):
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


class SpecificLocationAdmin(admin.ModelAdmin):
    form = ToponomikonKnownForm
    list_display = ['name', 'location_type', 'general_location', 'description']
    list_editable = ['location_type', 'general_location', 'description']
    list_filter = ['general_location__name']
    list_select_related = ['location_type', 'general_location', 'main_image']
    search_fields = ['name', 'description']

    def formfield_for_dbfield(self, db_field, **kwargs):
        # https://blog.ionelmc.ro/2012/01/19/tweaks-for-making-django-admin-faster/
        # Reduces greatly queries in main view, doubles in detail view
        # The trade-off is still very good
        request = kwargs['request']
        formfield = super().formfield_for_dbfield(db_field, **kwargs)
       
        if db_field.name in 'location_type':
            choices = getattr(request, '_location_type_choices_cache', None)
            if choices is None:
                request._main_location_type_cache = choices = list(
                    formfield.choices)
            formfield.choices = choices
    
        if db_field.name == 'general_location':
            choices = getattr(request, '_general_location_choices_cache', None)
            if choices is None:
                request._main_general_location_cache = choices = list(
                    formfield.choices)
            formfield.choices = choices
    
        return formfield


class SpecificLocationInline(admin.TabularInline):
    # TODO hundreds of queries due to inlines - optimize django admin inline
    model = SpecificLocation
    extra = 0

    form = ToponomikonKnownForm
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 15, 'cols': 25})},
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
    
        if db_field.name == 'general_location':
            choices = getattr(request, '_general_location_choices_cache', None)
            if choices is None:
                request._main_general_location_cache = choices = list(
                    formfield.choices)
            formfield.choices = choices
            
        return formfield
        

class GeneralLocationAdmin(admin.ModelAdmin):
    form = ToponomikonKnownForm
    inlines = [SpecificLocationInline]
    list_display = ['name', 'location_type', 'description', 'main_image']
    list_editable = ['location_type', 'description', 'main_image']
    list_select_related = ['main_image', 'location_type']
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
                request._main_image_choices_cache = choices = list(
                    formfield.choices)
            formfield.choices = choices

        if db_field.name == 'location_type':
            choices = getattr(request, '_location_type_choices_cache', None)
            if choices is None:
                request._main_location_type_cache = choices = list(
                    formfield.choices)
            formfield.choices = choices

        return formfield
    

class LocationTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'default_img']
    list_editable = ['default_img']
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
admin.site.register(GeneralLocation, GeneralLocationAdmin)
admin.site.register(SpecificLocation, SpecificLocationAdmin)
