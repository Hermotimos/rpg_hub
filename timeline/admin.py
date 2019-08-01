from django.contrib import admin
from django.forms import TextInput, Textarea
from django.db import models
from timeline.models import GameSession, Thread, GeneralLocation, SpecificLocation, Event, EventNote, DescribedEvent, \
    DescribedEventNote

admin.site.register(Thread)
admin.site.register(GeneralLocation)
admin.site.register(SpecificLocation)


class InlineEvent(admin.TabularInline):
    model = Event
    extra = 2

    # override attrs of form field when rendered as Inline:
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 8, 'cols': 50})},
    }


admin.site.register(Event)
admin.site.register(EventNote)
admin.site.register(DescribedEventNote)


class InlineDescribedEvent(admin.TabularInline):
    model = DescribedEvent
    extra = 2


class GameSessionAdmin(admin.ModelAdmin):
    inlines = [InlineDescribedEvent, InlineEvent]


admin.site.register(GameSession, GameSessionAdmin)


class DescribedEventAdmin(admin.ModelAdmin):

    # fields to be displayed in admin for each object
    fields = [
        'game_no',
        'event_no_in_game',
        'description',
        'participants',
        'informed'
    ]

    # list of fields to show in overview table (cannot include M2M fields)
    list_display = [
        'game_no',
        'event_no_in_game',
        'shorten_description',
    ]

    # way of customizing display of fields:
    def shorten_description(self, obj):
        return f'{obj.description[:100]}...{obj.description[-100:] if len(obj.description) > 200 else obj.description}'

    # fields may be made links leading to their objects:
    list_display_links = [
        'game_no',
        'shorten_description',
    ]

    # fields made ditable directly in list display:
    list_editable = [
        'event_no_in_game',
    ]

    list_filter = [
        'participants',
        'informed',
        'game_no',
    ]


admin.site.register(DescribedEvent, DescribedEventAdmin)

