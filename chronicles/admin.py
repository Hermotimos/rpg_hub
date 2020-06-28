from django.contrib import admin

from chronicles.models import Thread, Date, EventType, Event, ChronologySystem, \
    Era, Period, SingularEvent, Chapter, GameSession, GameEvent

# Event model
admin.site.register(Thread)
admin.site.register(Date)
admin.site.register(EventType)
admin.site.register(Event)

# Event proxies
admin.site.register(ChronologySystem)
admin.site.register(Era)
admin.site.register(Period)
admin.site.register(SingularEvent)

# GameEvent model
admin.site.register(Chapter)
admin.site.register(GameSession)
admin.site.register(GameEvent)

