from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.db import models
from django.db.models import Q
from django.forms import Textarea, TextInput, Select, SelectMultiple

from chronicles.models import Thread, Date, TimeUnit, Chronology, \
    Era, Period, HistoryEvent, Chapter, GameSession, GameEvent
from imaginarion.models import Picture
from toponomikon.models import Location
from users.models import Profile


class GameEventAdminForm(forms.ModelForm):
    class Meta:
        model = GameEvent
        fields = ['event_no_in_game', 'date_start', 'date_end', 'in_timeunit',
                  'description_short', 'description_long', 'threads',
                  'locations', 'known_directly', 'known_indirectly',
                  'pictures', 'debate', ]
        widgets = {
            'known_directly': FilteredSelectMultiple(
                'Known directly', False, attrs={'style': 'height:100px'}
            ),
            'known_indirectly': FilteredSelectMultiple(
                'Known indirectly', False, attrs={'style': 'height:100px'}
            ),
            'locations': FilteredSelectMultiple(
                'Locations', False, attrs={'style': 'height:100px'}
            ),
            'pictures': FilteredSelectMultiple(
                'Pictures', False, attrs={'style': 'height:100px'}
            ),
            'threads': FilteredSelectMultiple(
                'Threads', False, attrs={'style': 'height:100px'}
            ),
        }
        

class ChapterAdmin(admin.ModelAdmin):
    list_display = ['chapter_no', 'title', 'image']
    list_editable = ['title', 'image']
    search_fields = ['title']
    select_related = ['image']


class ThreadAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'is_ended']
    list_editable = ['name', 'is_ended']
    search_fields = ['name']


class GameEventInline(admin.TabularInline):
    model = GameEvent
    fields = ['event_no_in_game', 'date_start', 'date_end', 'in_timeunit',
              'description_short', 'description_long', 'threads', 'locations',
              'known_directly', 'known_indirectly', 'pictures', 'debate', ]
    extra = 3
    form = GameEventAdminForm
    list_select_related = ['chapter__image', 'date_start', 'date_end', 'in_timeunit', 'debate']
    
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 12, 'cols': 45})},
        models.CharField: {'widget': TextInput(attrs={'size': 15})},
        models.ForeignKey: {'widget': Select(attrs={'style': 'width:180px'})},
        models.OneToOneField: {'widget': Select(attrs={'style': 'width:200px'})},
    }
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        # https://blog.ionelmc.ro/2012/01/19/tweaks-for-making-django-admin-faster/
        # Reduces greatly queries in main view, doubles in detail view
        # The trade-off is still very good
        request = kwargs['request']
        formfield = super().formfield_for_dbfield(db_field, **kwargs)
        
        if db_field.name == 'date_start':
            choices = getattr(request, '_date_start_choices_cache', None)
            if choices is None:
                request._main_date_start_cache = choices = list(
                    formfield.choices)
            formfield.choices = choices
            
        if db_field.name == 'date_end':
            choices = getattr(request, '_date_end_choices_cache', None)
            if choices is None:
                request._main_date_end_cache = choices = list(
                    formfield.choices)
            formfield.choices = choices
            
        if db_field.name == 'in_timeunit':
            choices = getattr(request, '_in_timeunit_choices_cache', None)
            if choices is None:
                request._main_in_timeunit_cache = choices = list(
                    formfield.choices)
            formfield.choices = choices
        
        if db_field.name == 'debate':
            choices = getattr(request, '_debate_choices_cache',
                              None)
            if choices is None:
                request._main_debate_cache = choices = list(
                    formfield.choices)
            formfield.choices = choices

        if db_field.name == 'known_directly':
            choices = getattr(request, '_known_directly_choices_cache', None)
            if choices is None:
                request._main_known_directly_cache = choices = list(
                    formfield.choices)
            formfield.choices = choices
        
        if db_field.name == 'known_indirectly':
            choices = getattr(request, '_known_indirectly_choices_cache', None)
            if choices is None:
                request._main_known_indirectly_cache = choices = list(
                    formfield.choices)
            formfield.choices = choices
            
        if db_field.name == 'locations':
            choices = getattr(request, '_locations_choices_cache', None)
            if choices is None:
                request._main_locations_cache = choices = list(
                    formfield.choices)
            formfield.choices = choices
        
        if db_field.name == 'threads':
            choices = getattr(request, '_threads_choices_cache', None)
            if choices is None:
                request._main_threads_cache = choices = list(
                    formfield.choices)
            formfield.choices = choices

        if db_field.name == 'pictures':
            choices = getattr(request, '_pictures_choices_cache',
                              None)
            if choices is None:
                request._main_pictures_cache = choices = list(
                    formfield.choices)
            formfield.choices = choices

        return formfield

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.prefetch_related(
            'known_directly',
            'known_indirectly',
            'threads',
            'locations',
            'pictures',
            'in_timeunit',
        )
        return qs


class GameSessionAdmin(admin.ModelAdmin):
    inlines = [GameEventInline]
    list_display = ['game_no', 'title', 'chapter', 'date']
    list_editable = ['title', 'chapter', 'date']
    list_select_related = ['chapter']
    search_fields = ['title']

    def formfield_for_dbfield(self, db_field, **kwargs):
        # https://blog.ionelmc.ro/2012/01/19/tweaks-for-making-django-admin-faster/
        request = kwargs['request']
        formfield = super().formfield_for_dbfield(db_field, **kwargs)

        if db_field.name == 'chapter':
            choices = getattr(request, '_chapter_choices_cache', None)
            if choices is None:
                request._chapter_choices_cache = choices = list(
                    formfield.choices)
            formfield.choices = choices

        return formfield
    
    
    
# Side models
admin.site.register(Thread, ThreadAdmin)
admin.site.register(Date)
admin.site.register(Chapter, ChapterAdmin)
admin.site.register(GameSession, GameSessionAdmin)

# TimeUnit model
admin.site.register(TimeUnit)

# TimeUnit proxies
admin.site.register(Chronology)
admin.site.register(Era)
admin.site.register(Period)
admin.site.register(HistoryEvent)
admin.site.register(GameEvent)


