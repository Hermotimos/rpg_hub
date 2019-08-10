from django.contrib import admin
from imaginarion.models import Picture


class PictureAdmin(admin.ModelAdmin):
    list_display = ('admin_title', 'description', 'image')
    list_editable = ('description', 'image')


admin.site.register(Picture, PictureAdmin)
