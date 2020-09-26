from django.contrib import admin
from django.db.models import Case, When, Value
from django.utils.html import format_html

from .models import Profile


class ProfileAdmin(admin.ModelAdmin):
    list_display = ['get_img', 'user', 'character_name', 'status', 'image']
    list_editable = ['character_name', 'status', 'image']
    list_filter = ['status']
    search_fields = ['user', 'character_name']

    def get_img(self, obj):
        if obj.image:
            return format_html(
                f'<img src="{obj.image.url}" width="70" height="70">'
            )
        default_img = "media/profile_pics/profile_default.jpg"
        return format_html(f'<img src={default_img} width="70" height="70">')


admin.site.register(Profile, ProfileAdmin)
