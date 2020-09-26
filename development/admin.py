from django.contrib import admin
from development.models import ProfileKlass, Achievement
from django.utils.html import format_html


class ProfileKlassAdmin(admin.ModelAdmin):
    list_display = ['get_img', 'klass', 'experience']
    list_editable = ['experience', ]
    list_filter = ['profile', 'klass']
    search_fields = ['profile', 'klass']

    def get_img(self, obj):
        if obj.profile.image:
            return format_html(
                f'<img src="{obj.profile.image.url}" width="70" height="70">'
            )
        default_img = "media/profile_pics/profile_default.jpg"
        return format_html(f'<img src={default_img} width="70" height="70">')


class AchievementAdmin(admin.ModelAdmin):
    list_display = ['get_img', 'name', 'description']
    list_editable = ['name', 'description']
    list_filter = ['name', 'description']
    search_fields = ['profile']

    def get_img(self, obj):
        if obj.profile.image:
            return format_html(
                f'<img src="{obj.profile.image.url}" width="70" height="70">'
            )
        default_img = "media/profile_pics/profile_default.jpg"
        return format_html(f'<img src={default_img} width="70" height="70">')


admin.site.register(ProfileKlass, ProfileKlassAdmin)
admin.site.register(Achievement, AchievementAdmin)
