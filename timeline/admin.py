from django.contrib import admin
from timeline.models import Thread, GameSession, GeneralLocation, SpecificLocation, Event, EventNote, \
    DescribedEvent

admin.site.register(Thread)
admin.site.register(GameSession)
admin.site.register(GeneralLocation)
admin.site.register(SpecificLocation)
admin.site.register(Event)
admin.site.register(EventNote)
admin.site.register(DescribedEvent)
