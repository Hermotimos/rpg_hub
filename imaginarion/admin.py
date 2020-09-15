from django.contrib import admin
from imaginarion.models import Picture, Audio


class AudioAdmin(admin.ModelAdmin):
    list_display = ['id', 'admin_title', 'type', 'path']
    list_editable = ['type', 'path']
    list_filter = ['type']
    search_fields = ['title']
    
    def admin_title(self, obj):
        return obj.__str__()
    
    
class PictureAdmin(admin.ModelAdmin):
    list_display = ['id', 'admin_title', 'type', 'description', 'image']
    list_editable = ['type', 'description', 'image']
    search_fields = ['title', 'description']

    def admin_title(self, obj):
        return obj.__str__()


admin.site.register(Audio, AudioAdmin)
admin.site.register(Picture, PictureAdmin)
