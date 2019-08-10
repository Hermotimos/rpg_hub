from django.contrib import admin
from imaginarion.models import Picture


class PictureAdmin(admin.ModelAdmin):
    list_display = ('admin_title', 'description')


admin.site.register(Picture, PictureAdmin)
