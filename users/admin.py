from django.contrib import admin
from .models import Profile


class ProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'character_name', 'character_status', 'image']
    list_editable = ['character_name', 'character_status', 'image']
    list_filter = ['character_status']
    search_fields = ['character_name']


admin.site.register(Profile, ProfileAdmin)
