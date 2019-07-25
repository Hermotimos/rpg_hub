from django.contrib import admin
from timeline.models import Thread, GameSession, GeneralLocation, SpecificLocation, Event, EventNote, \
    DescribedEvent, DescribedEventNote

admin.site.register(Thread)
admin.site.register(GameSession)
admin.site.register(GeneralLocation)
admin.site.register(SpecificLocation)
admin.site.register(Event)
admin.site.register(EventNote)


class DescribedEventAdmin(admin.ModelAdmin):
    list_display = [
        'game_no',
        'event_no_in_game',
        'description',
    ]


admin.site.register(DescribedEvent, DescribedEventAdmin)
admin.site.register(DescribedEventNote)
