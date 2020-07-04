from django.contrib import admin

from chronicles.models import Thread, Date, TimeUnit, Chronology, \
    Era, Period, HistoryEvent, Chapter, GameSession, GameEvent

# Side models
admin.site.register(Thread)
admin.site.register(Date)
admin.site.register(Chapter)
admin.site.register(GameSession)

# TimeUnit model
admin.site.register(TimeUnit)

# TimeUnit proxies
admin.site.register(Chronology)
admin.site.register(Era)
admin.site.register(Period)
admin.site.register(HistoryEvent)
admin.site.register(GameEvent)

