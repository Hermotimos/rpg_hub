from django.contrib import admin
from django.db.models import TextField
from django.forms import Textarea

from imaginarion.models import Picture, PictureImage, Audio, AudioSet


class AudioAdmin(admin.ModelAdmin):
    formfield_overrides = {
        TextField: {'widget': Textarea(attrs={'rows': 8, 'cols': 50})},
    }
    list_display = ['id', 'admin_title', 'type', 'description', 'path']
    list_editable = ['type', 'description', 'path']
    list_filter = ['type']
    search_fields = ['title', 'description']
    
    def admin_title(self, obj):
        return obj.__str__()
    
    
class AudioSetAdmin(admin.ModelAdmin):
    formfield_overrides = {
        TextField: {'widget': Textarea(attrs={'rows': 8, 'cols': 50})},
    }
    list_display = ['id', 'title', 'description', 'main_audio']
    list_editable = ['title', 'description', 'main_audio']
    search_fields = ['title', 'description', 'main_audio']
    
    
class PictureAdmin(admin.ModelAdmin):
    list_display = ['id', 'type', 'description', 'image']
    list_editable = ['type', 'description']
    list_filter = ['type']
    search_fields = ['title', 'description']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related('image')
        return qs
    
    
class PictureImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'description', 'image', 'sorting_name']
    list_editable = ['description', 'image']
    search_fields = ['image', 'description']
    

admin.site.register(Audio, AudioAdmin)
admin.site.register(AudioSet, AudioSetAdmin)
admin.site.register(Picture, PictureAdmin)
admin.site.register(PictureImage, PictureImageAdmin)
