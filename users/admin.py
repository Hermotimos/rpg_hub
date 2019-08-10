from django.contrib import admin
from .models import Profile


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('character_name', 'character_status', 'image')
    list_editable = ('character_status', 'image')
    list_filter = ('character_status',)


admin.site.register(Profile, ProfileAdmin)
