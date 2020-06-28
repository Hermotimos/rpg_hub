from django.contrib import admin

from chronicles.models import Date, EventType, Event, ChronologySystem, Era, Period


admin.site.register(Date)
admin.site.register(EventType)
admin.site.register(Event)

# Event proxies
admin.site.register(ChronologySystem)
admin.site.register(Era)
admin.site.register(Period)

