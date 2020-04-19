from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.db import models
from django.db.models import Q
from django.forms import Textarea
from django.utils.html import format_html

from history.models import (Chapter,
                            GameSession,
                            Thread,
                            TimelineEvent,
                            ChronicleEvent)
from imaginarion.models import Picture
from toponomikon.models import GeneralLocation, SpecificLocation
from users.models import Profile


class ChronicleEventAdminForm(forms.ModelForm):
    participants = forms.ModelMultipleChoiceField(
        queryset=Profile.objects.exclude(Q(status='dead_player')
                                         | Q(status='dead_npc')
                                         | Q(status='gm')
                                         | Q(status='living_npc')),
        required=False,
        widget=FilteredSelectMultiple('Participants', False),
    )
    informed = forms.ModelMultipleChoiceField(
        queryset=Profile.objects.exclude(Q(status='dead_player')
                                         | Q(status='dead_npc')
                                         | Q(status='gm')
                                         | Q(status='living_npc')),
        required=False,
        widget=FilteredSelectMultiple('Informed', False),
    )
    pictures = forms.ModelMultipleChoiceField(
        queryset=Picture.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('Pictures', False),
    )


class TimelineEventAdminForm(forms.ModelForm):
    participants = forms.ModelMultipleChoiceField(
        queryset=Profile.objects.exclude(Q(status='dead_player')
                                         | Q(status='dead_npc')
                                         | Q(status='gm')
                                         | Q(status='living_npc')),
        required=False,
        widget=FilteredSelectMultiple('Participants', False),
    )
    informed = forms.ModelMultipleChoiceField(
        queryset=Profile.objects.exclude(Q(status='dead_player')
                                         | Q(status='dead_npc')
                                         | Q(status='gm')
                                         | Q(status='living_npc')),
        required=False,
        widget=FilteredSelectMultiple('Informed', False),
    )
    threads = forms.ModelMultipleChoiceField(
        queryset=Picture.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('Threads', False),
    )
    general_locations = forms.ModelMultipleChoiceField(
        queryset=GeneralLocation.objects.all(),
        required=True,
        widget=FilteredSelectMultiple('General locations', False),
    )
    specific_locations = forms.ModelMultipleChoiceField(
        queryset=SpecificLocation.objects.all(),
        required=True,
        widget=FilteredSelectMultiple('Specific locations', False),
    )


class ChapterAdmin(admin.ModelAdmin):
    list_display = ['chapter_no', 'title', 'image']
    list_editable = ['title', 'image']
    search_fields = ['title']


class TimelineEventInline(admin.TabularInline):
    model = TimelineEvent
    extra = 3

    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 8, 'cols': 50})},
    }

    def formfield_for_dbfield(self, db_field, **kwargs):
        # https://blog.ionelmc.ro/2012/01/19/tweaks-for-making-django-admin-faster/
        # Reduces greatly queries in main view, doubles in detail view
        # The trade-off is still very good
        request = kwargs['request']
        formfield = super().formfield_for_dbfield(db_field, **kwargs)

        if db_field.name == 'participants':
            choices = getattr(request, '_participants_choices_cache', None)
            if choices is None:
                request._main_participants_cache = choices = list(
                    formfield.choices)
            formfield.choices = choices
            
        if db_field.name == 'informed':
            choices = getattr(request, '_informed_choices_cache', None)
            if choices is None:
                request._main_informed_cache = choices = list(
                    formfield.choices)
            formfield.choices = choices

        if db_field.name == 'general_locations':
            choices = getattr(request, '_general_locations_choices_cache', None)
            if choices is None:
                request._main_general_locations_cache = choices = list(
                    formfield.choices)
            formfield.choices = choices

        if db_field.name == 'specific_locations':
            choices = getattr(request, '_specific_locations_choices_cache', None)
            if choices is None:
                request._main_specific_locations_cache = choices = list(
                    formfield.choices)
            formfield.choices = choices

        if db_field.name == 'threads':
            choices = getattr(request, '_threads_choices_cache', None)
            if choices is None:
                request._main_threads_cache = choices = list(
                    formfield.choices)
            formfield.choices = choices

        return formfield
    

class ChronicleEventInline(admin.TabularInline):
    model = ChronicleEvent
    extra = 2

    def formfield_for_dbfield(self, db_field, **kwargs):
        # https://blog.ionelmc.ro/2012/01/19/tweaks-for-making-django-admin-faster/
        # Reduces greatly queries in main view, doubles in detail view
        # The trade-off is still very good
        request = kwargs['request']
        formfield = super().formfield_for_dbfield(db_field, **kwargs)
    
        if db_field.name == 'participants':
            choices = getattr(request, '_participants_choices_cache', None)
            if choices is None:
                request._main_participants_cache = choices = list(
                    formfield.choices)
            formfield.choices = choices
    
        if db_field.name == 'informed':
            choices = getattr(request, '_informed_choices_cache', None)
            if choices is None:
                request._main_informed_cache = choices = list(
                    formfield.choices)
            formfield.choices = choices
    
        if db_field.name == 'pictures':
            choices = getattr(request, '_pictures_choices_cache',
                              None)
            if choices is None:
                request._main_pictures_cache = choices = list(
                    formfield.choices)
            formfield.choices = choices
    
        if db_field.name == 'debate':
            choices = getattr(request, '_debate_choices_cache',
                              None)
            if choices is None:
                request._main_debate_cache = choices = list(
                    formfield.choices)
            formfield.choices = choices
    
        return formfield


class ChronicleEventAdmin(admin.ModelAdmin):
    fields = ['game', 'event_no_in_game', 'description', 'participants',
              'informed', 'pictures', 'debate']
    form = ChronicleEventAdminForm
    list_display = ['game', 'event_no_in_game', 'short_description']
    list_display_links = ['short_description']
    list_editable = ['event_no_in_game']
    list_filter = ['participants', 'informed', 'game']
    search_fields = ['description']


class GameSessionAdmin(admin.ModelAdmin):
    inlines = [TimelineEventInline, ChronicleEventInline]
    list_display = ['id', 'game_no', 'title', 'chapter', 'date']
    list_editable = ['game_no', 'title', 'chapter', 'date']
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
    

class TimelineEventAdmin(admin.ModelAdmin):
    form = TimelineEventAdminForm
    list_display = ['short_description', 'game', 'date']
    list_filter = ['game']
    search_fields = ['description']


class ThreadAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'is_ended']
    list_editable = ['name', 'is_ended']
    search_fields = ['name']


admin.site.register(Chapter, ChapterAdmin)
admin.site.register(Thread, ThreadAdmin)
admin.site.register(GameSession, GameSessionAdmin)
admin.site.register(TimelineEvent, TimelineEventAdmin)
admin.site.register(ChronicleEvent, ChronicleEventAdmin)


