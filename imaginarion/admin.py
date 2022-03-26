from django import forms
from django.contrib import admin
from django.db import models
from django.utils.html import format_html

from imaginarion.models import Picture, PictureImage, PictureSet, Audio, AudioSet
from rpg_project.utils import formfield_with_cache


# -----------------------------------------------------------------------------


@admin.register(Audio)
class AudioAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(attrs={'rows': 8, 'cols': 50})},
    }
    list_display = ['id', 'admin_title', 'type', 'description', 'path']
    list_editable = ['type', 'description', 'path']
    list_filter = ['type']
    search_fields = ['title', 'description']
    
    def admin_title(self, obj):
        return obj.__str__()
    
    
@admin.register(AudioSet)
class AudioSetAdmin(admin.ModelAdmin):
    filter_horizontal = ['audios']
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(attrs={'rows': 8, 'cols': 50})},
    }
    list_display = ['id', 'title', 'description', 'main_audio']
    list_editable = ['title', 'description', 'main_audio']
    search_fields = ['title', 'description', 'main_audio']
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        for field in [
            'main_audio',
        ]:
            if db_field.name == field:
                formfield = formfield_with_cache(field, formfield, request)
        return formfield

    
# -----------------------------------------------------------------------------


@admin.register(Picture)
class PictureAdmin(admin.ModelAdmin):
    list_display = ['id', 'type', 'description', 'get_image']
    list_editable = ['type', 'description']
    list_filter = ['type']
    search_fields = ['description']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related('image')
        return qs
    
    def get_image(self, obj):
        html = f'<img height="60" src="{obj.image.image.url}">&nbsp;'
        return format_html(html)

    
@admin.register(PictureImage)
class PictureImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'description', 'image', 'sorting_name']
    list_editable = ['description', 'image']
    search_fields = ['description', 'sorting_name']


@admin.register(PictureSet)
class PictureSetAdmin(admin.ModelAdmin):
    filter_horizontal = ['pictures']
    list_display = ['id', 'title', 'images']
    list_editable = ['title']
    search_fields = ['title']

    def images(self, obj):
        picture_imgs_urls = [p.image.image.url for p in obj.pictures.all()]
        html = ''
        if picture_imgs_urls:
            for url in picture_imgs_urls:
                html += f'<img height="40" src="{url}">&nbsp;'
        else:
            html = '<h1><font color="red">BRAK OBRAZÓW</font></h1>'
        return format_html(html)
