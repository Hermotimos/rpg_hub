from django.contrib import admin
from prosoponomikon.models import Character, PlayerCharacter, NonPlayerCharacter, CharacterGroup

admin.site.register(CharacterGroup)
admin.site.register(Character)
admin.site.register(PlayerCharacter)
admin.site.register(NonPlayerCharacter)
