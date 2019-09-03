from django.contrib import admin
from django.forms import Textarea
from django.db import models
from history.models import (Chapter,
                            GameSession,
                            Thread,
                            GeneralLocation,
                            SpecificLocation,
                            TimelineEvent,
                            TimelineEventNote,
                            ChronicleEvent,
                            ChronicleEventNote)


class ThreadAdmin(admin.ModelAdmin):
    model = Thread
    list_display = ['name', 'is_ended']
    list_editable = ['is_ended', ]


class TimelineEventInline(admin.TabularInline):
    model = TimelineEvent
    extra = 3

    # override attrs of form field when rendered as Inline:
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 8, 'cols': 50})},
    }


class ChronicleEventInline(admin.TabularInline):
    model = ChronicleEvent
    extra = 2


class GameSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'game_no', 'title', 'chapter', 'date']
    list_editable = ['game_no', 'title', 'chapter', 'date']
    inlines = [TimelineEventInline, ChronicleEventInline]


class SpecificLocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'general_location']
    list_editable = ['general_location', ]
    list_filter = ['general_location', ]


class TimelineEventAdmin(admin.ModelAdmin):
    list_display = ('short_description', 'game', 'date')
    list_filter = ('game', )


class ChronicleEventAdmin(admin.ModelAdmin):

    # fields to be displayed in admin for each object
    fields = ['game', 'event_no_in_game', 'description', 'participants', 'informed', 'pictures', 'debate']

    # list of fields to show in overview table (cannot include M2M fields)
    list_display = ['game', 'event_no_in_game', 'short_description']

    # fields may be made links leading to their objects:
    list_display_links = ['game', 'short_description']

    # fields made editable directly in list display:
    list_editable = ['event_no_in_game', ]

    list_filter = ['participants', 'informed', 'game', ]


admin.site.register(Chapter)
admin.site.register(Thread, ThreadAdmin)
admin.site.register(GameSession, GameSessionAdmin)
admin.site.register(GeneralLocation)
admin.site.register(SpecificLocation, SpecificLocationAdmin)
admin.site.register(TimelineEvent, TimelineEventAdmin)
admin.site.register(TimelineEventNote)
admin.site.register(ChronicleEvent, ChronicleEventAdmin)
admin.site.register(ChronicleEventNote)


