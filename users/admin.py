from django.contrib import admin
from django.utils.html import format_html

from users.models import Profile


class ProfileAdmin(admin.ModelAdmin):
    list_display = ['get_img', 'user', 'status', 'is_alive', 'is_active', 'image']
    list_editable = ['status', 'is_alive', 'is_active', 'image']
    list_filter = ['status', 'is_alive', 'is_active']
    search_fields = ['user', 'name']

    def get_img(self, obj):
        if obj.image:
            return format_html(
                f'<img src="{obj.image.url}" width="70" height="70">')
        default_img = "media/profile_pics/profile_default.jpg"
        return format_html(f'<img src={default_img} width="70" height="70">')


admin.site.register(Profile, ProfileAdmin)
