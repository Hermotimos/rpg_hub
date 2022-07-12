from django import forms
from django.contrib import admin
from django.db import models

from chronicles.models import (
    PlotThread,
    Date,
    TimeUnit, Chronology, Era, Period, HistoryEvent, GameEvent,
    Chapter,
    GameSession,
)
from communications.models import Thread
from rpg_project.utils import formfield_with_cache
from toponomikon.models import Location
from users.models import Profile


# -----------------------------------------------------------------------------


@admin.register(Date)
class DateAdmin(admin.ModelAdmin):
    pass


# -----------------------------------------------------------------------------


@admin.register(HistoryEvent)
class HistoryEventAdmin(admin.ModelAdmin):
    fields = [
        'date_start', 'date_end', 'in_timeunit', 'description_short',
        'description_long', 'plot_threads', 'locations',
        'known_short_desc', 'known_long_desc'
    ]
    filter_horizontal = [
        'known_short_desc', 'known_long_desc', 'locations', 'picture_sets',
        'plot_threads'
    ]
    list_display = [
        'id', 'date_in_period', 'date_in_era', 'date_in_chronology',
        'description_short', 'description_long', 'audio'
    ]
    list_editable = ['description_short', 'description_long', 'audio']
    search_fields = ['description_short', 'description_long']
    
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name in ["known_short_desc", "known_long_desc"]:
            kwargs["queryset"] = Profile.non_gm.all()
        return super().formfield_for_manytomany(db_field, request, **kwargs)


# -----------------------------------------------------------------------------


@admin.register(GameEvent)
class GameEventAdmin(admin.ModelAdmin):
    fields = (
        ('game', 'event_no_in_game'), ('date_start', 'date_end'), 'in_timeunit',
        ('description_short', 'description_long'), 'plot_threads', 'locations',
        'participants', 'informees', 'picture_sets', 'debates', 'audio'
    )
    filter_horizontal = [
        'participants', 'informees', 'locations', 'picture_sets',
        'plot_threads', 'debates',
    ]
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(attrs={'rows': 12, 'cols': 35})},
        models.ForeignKey: {'widget': forms.Select(attrs={'style': 'width:140px'})},
    }
    list_display = [
        'id', 'game', 'event_no_in_game', 'date_in_period',
        'description_short', 'description_long', 'audio'
    ]
    list_editable = [
        'event_no_in_game', 'description_short', 'description_long', 'audio'
    ]
    list_filter = ['game']
    search_fields = ['description_short', 'description_long']
    
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name in ["participants", "informees"]:
            kwargs["queryset"] = Profile.non_gm.select_related('character')
        if db_field.name == "debates":
            kwargs["queryset"] = Thread.objects.filter(kind='Debate')
        return super().formfield_for_manytomany(db_field, request, **kwargs)
        
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        for field in [
            'audio',  # Tested that here only audio optimizes queries
        ]:
            if db_field.name == field:
                formfield = formfield_with_cache(field, formfield, request)
        return formfield


# -----------------------------------------------------------------------------


class GameEventInline(admin.TabularInline):
    model = GameEvent
    extra = 0
    fields = [
        'game', 'event_no_in_game', 'date_start', 'date_end', 'in_timeunit',
        'description_short', 'description_long', 'plot_threads', 'locations',
        'participants', 'informees', 'picture_sets', 'debates', 'audio'
    ]
    filter_horizontal = [
        'participants', 'informees', 'locations', 'picture_sets',
        'plot_threads', 'debates',
    ]
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(attrs={'rows': 12, 'cols': 45})},
        models.CharField: {'widget': forms.TextInput(attrs={'size': 15})},
        models.ForeignKey: {'widget': forms.Select(attrs={'style': 'width:180px'})},
        models.OneToOneField: {'widget': forms.Select(attrs={'style': 'width:200px'})},
    }

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        # Filter querysets before calling super(), otherwise it has no effect
        if db_field.name in ["participants", "informees"]:
            kwargs["queryset"] = Profile.non_gm.all()
        if db_field.name == "debates":
            kwargs["queryset"] = Thread.objects.filter(kind='Debate')

        form_field = super().formfield_for_manytomany(db_field, request, **kwargs)
        for field in [
            'participants',
            'informees',
            'locations',
            'plot_threads',
            'picture_sets',
            'debates',
        ]:
            if db_field.name == field:
                form_field = formfield_with_cache(field, form_field, request)
                form_field.widget.attrs = {'style': 'height:150px'}

        return form_field

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        for field in [
            'date_start',
            'date_end',
            'in_timeunit',
            'audio',
        ]:
            if db_field.name == field:
                formfield = formfield_with_cache(field, formfield, request)
        return formfield
    

# -----------------------------------------------------------------------------


@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.CharField: {'widget': forms.TextInput(attrs={'size': 70})},
    }
    inlines = [GameEventInline]
    list_display = ['game_no', 'title', 'chapter', 'date']
    list_editable = ['title', 'chapter', 'date']
    list_select_related = ['chapter']
    ordering = ['-game_no']
    search_fields = ['title']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        for field in [
            'chapter',
        ]:
            if db_field.name == field:
                formfield = formfield_with_cache(field, formfield, request)
        return formfield


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ['chapter_no', 'title', 'image']
    list_editable = ['title', 'image']
    search_fields = ['title']
    select_related = ['image']


@admin.register(PlotThread)
class PlotThreadAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'is_ended']
    list_editable = ['name', 'is_ended']
    list_filter = ['is_ended']
    search_fields = ['name']


# -----------------------------------------------------------------------------


# @admin.register(TimeUnit)
# class TimeUnitAdmin(admin.ModelAdmin):
#     list_display = ['id', 'description_short', 'description_long']
#     search_fields = ['description_short', 'description_long']
    

@admin.register(Chronology)
class ChronologyAdmin(admin.ModelAdmin):
    fields = [
        'name', 'name_genetive', 'date_start', 'date_end', 'description_short',
        'description_long', 'known_short_desc', 'known_long_desc',
    ]
    filter_horizontal = ['known_short_desc', 'known_long_desc']


@admin.register(Era, Period)
class EraAndPeriodAdmin(admin.ModelAdmin):
    fields = [
        'name', 'name_genetive', 'date_start', 'date_end', 'description_short',
        'description_long', 'known_short_desc', 'known_long_desc',
        'in_timeunit',
    ]
    filter_horizontal = ['known_short_desc', 'known_long_desc']
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(attrs={'rows': 15, 'cols': 40})},
        models.CharField: {'widget': forms.TextInput(attrs={'size': 12})},
        models.ForeignKey: {'widget': forms.Select(attrs={'style': 'width:180px'})},
    }
    list_display = [
        'id', 'name', 'name_genetive', 'date_start', 'date_end', 'in_timeunit',
        'description_short', 'description_long'
    ]
    list_editable = [
        'name', 'name_genetive', 'date_start', 'date_end', 'in_timeunit',
        'description_short', 'description_long'
    ]
    search_fields = [
        'name', 'name_genetive', 'description_short', 'description_long'
    ]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        for field in [
            'date_start',
            'date_end',
            'in_timeunit',
        ]:
            if db_field.name == field:
                formfield = formfield_with_cache(field, formfield, request)
        return formfield

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "in_timeunit":
            kwargs["queryset"] = Chronology.objects.all()
        if db_field.name == "locations":
            kwargs["queryset"] = Location.objects.filter(location_type__name='Kraina')
        return super().formfield_for_manytomany(db_field, request, **kwargs)
