from django.contrib import admin
from django.utils.html import format_html
from .models import Profile


class ProfileAdmin(admin.ModelAdmin):
    list_display = ['get_img', 'user', 'character_name', 'status', 'image']
    list_editable = ['character_name', 'status', 'image']
    list_filter = ['status']
    search_fields = ['user', 'character_name']

    def get_img(self, obj):
        if obj.image:
            return format_html(f'<img width="40" height="40" src="{obj.image.url}">')
        return format_html(f'<img width="40" height="40" src="media/profile_pics/profile_default.jpg">')


admin.site.register(Profile, ProfileAdmin)
