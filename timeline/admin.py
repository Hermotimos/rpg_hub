from django.contrib import admin
from timeline.models import Thread, GameSession, GeneralLocation, SpecificLocation, Event

admin.site.register(Thread)
admin.site.register(GameSession)
admin.site.register(GeneralLocation)
admin.site.register(SpecificLocation)
admin.site.register(Event)
