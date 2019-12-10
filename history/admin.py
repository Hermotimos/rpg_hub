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


class ChapterAdmin(admin.ModelAdmin):
    model = Chapter
    list_display = ['chapter_no', 'title', 'image']
    list_editable = ['title', 'image']
    search_fields = ['title']


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
    search_fields = ['title']


class SpecificLocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'general_location']
    list_editable = ['general_location', ]
    list_filter = ['general_location', ]
    search_fields = ['name']


class TimelineEventAdmin(admin.ModelAdmin):
    list_display = ['short_description', 'game', 'date']
    list_filter = ['game']
    search_fields = ['description']


class ChronicleEventAdmin(admin.ModelAdmin):

    # fields to be displayed in admin for each object
    fields = ['game', 'event_no_in_game', 'description', 'participants', 'informed', 'pictures', 'debate']

    list_display = ['game', 'event_no_in_game', 'short_description']
    list_display_links = ['game', 'short_description']
    list_editable = ['event_no_in_game', ]
    list_filter = ['participants', 'informed', 'game', ]
    search_fields = ['description']


class ChronicleEventNoteAdmin(admin.ModelAdmin):
    model = ChronicleEventNote
    list_display = ['id', 'author', 'text_short']
    search_fields = ['text']

    def text_short(self, obj):
        return f'{obj.text[:100]}...'


admin.site.register(Chapter, ChapterAdmin)
admin.site.register(Thread, ThreadAdmin)
admin.site.register(GameSession, GameSessionAdmin)
admin.site.register(GeneralLocation)
admin.site.register(SpecificLocation, SpecificLocationAdmin)
admin.site.register(TimelineEvent, TimelineEventAdmin)
admin.site.register(TimelineEventNote)
admin.site.register(ChronicleEvent, ChronicleEventAdmin)
admin.site.register(ChronicleEventNote, ChronicleEventNoteAdmin)


