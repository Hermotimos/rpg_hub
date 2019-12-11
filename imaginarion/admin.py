from django.contrib import admin
from imaginarion.models import Picture


class PictureAdmin(admin.ModelAdmin):
    list_display = ['admin_title', 'type', 'description', 'image']
    list_editable = ['description', 'image']
    search_fields = ['title', 'description']

    def admin_title(self, obj):
        return obj.__str__()


admin.site.register(Picture, PictureAdmin)
