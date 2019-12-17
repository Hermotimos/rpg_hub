from django.contrib import admin
from django.db import models
from django.forms import Textarea
from django.utils.html import format_html
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
    list_display = ['chapter_no', 'title', 'image']
    list_editable = ['title', 'image']
    search_fields = ['title']


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


class ChronicleEventAdmin(admin.ModelAdmin):
    # fields to be displayed in admin for each object
    fields = ['game', 'event_no_in_game', 'description', 'participants', 'informed', 'pictures', 'debate']

    list_display = ['game', 'event_no_in_game', 'short_description']
    list_display_links = ['short_description']
    list_editable = ['event_no_in_game', ]
    list_filter = ['participants', 'informed', 'game', ]
    search_fields = ['description']


class ChronicleEventNoteAdmin(admin.ModelAdmin):
    fields = ['author', 'event']
    list_display = ['id', 'author', 'text_secret']
    search_fields = ['text']

    def text_secret(self, obj):
        return format_html('<b><font color="red">TOP SECRET</font></b>')


class GameSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'game_no', 'title', 'chapter', 'date']
    list_editable = ['game_no', 'title', 'chapter', 'date']
    inlines = [TimelineEventInline, ChronicleEventInline]
    search_fields = ['title']


class TimelineEventAdmin(admin.ModelAdmin):
    list_display = ['short_description', 'game', 'date']
    list_filter = ['game']
    search_fields = ['description']


class TimelineEventNoteAdmin(admin.ModelAdmin):
    fields = ['author', 'event']
    list_display = ['id', 'author', 'text_secret']
    search_fields = ['text']

    def text_secret(self, obj):
        return format_html('<b><font color="red">TOP SECRET</font></b>')


class ThreadAdmin(admin.ModelAdmin):
    model = Thread
    list_display = ['id', 'name', 'is_ended']
    list_editable = ['name', 'is_ended']
    search_fields = ['name']




admin.site.register(Chapter, ChapterAdmin)
admin.site.register(Thread, ThreadAdmin)
admin.site.register(GameSession, GameSessionAdmin)
admin.site.register(TimelineEvent, TimelineEventAdmin)
admin.site.register(TimelineEventNote, TimelineEventNoteAdmin)
admin.site.register(ChronicleEvent, ChronicleEventAdmin)
admin.site.register(ChronicleEventNote, ChronicleEventNoteAdmin)


