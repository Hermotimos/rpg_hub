from django.contrib import admin
from django.db import models
from django.utils.html import format_html

from characters.models import Character


class CharacterAdmin(admin.ModelAdmin):
    list_display = ['get_img']

    def get_img(self, obj):
        if obj.profile.image:
            return format_html(f'<img width="40" height="40" src="{obj.profile.image.url}">')
        else:
            return format_html(f'<img width="40" height="40" src="media/profile_pics/profile_default.jpg">')


admin.site.register(Character, CharacterAdmin)
