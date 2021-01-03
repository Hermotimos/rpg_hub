from django.contrib import admin
from prosoponomikon.models import Persona, PlayerPersona, NonPlayerPersona, PersonaGroup

admin.site.register(PersonaGroup)
admin.site.register(Persona)
admin.site.register(PlayerPersona)
admin.site.register(NonPlayerPersona)
