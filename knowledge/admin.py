from django.contrib import admin
from django.db.models import CharField, TextField
from django.forms.widgets import TextInput, Textarea
from django.utils.html import format_html

from knowledge.admin_forms import (
    DialoguePacketAdminForm,
    KnowledgePacketAdminForm,
    MapPacketAdminForm
)
# from associations.models import Comment
from knowledge.models import (
    Reference,
    KnowledgePacket,
    MapPacket,
    BiographyPacket,
    DialoguePacket
)

WARNING = """
    <b style="color:red">
        PRZY TWORZENIU NOWEGO PAKIETU ZAPIS POSTACI JEST NIEMOŻLIWY
        <br><br>
        PODAJ POSTACIE W DRUGIEJ TURZE :)
    </b>
"""

# -----------------------------------------------------------------------------


# class CommentInline(GenericTabularInline):
#     filter_horizontal = ['linked_comments']
#     model = Comment
#     extra = 2
#
#     def formfield_for_foreignkey(self, db_field, request, **kwargs):
#         formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
#         for field in [
#             'author',
#         ]:
#             if db_field.name == field:
#                 formfield = formfield_with_cache(field, formfield, request)
#         return formfield


# -----------------------------------------------------------------------------

        
@admin.register(Reference)
class ReferenceAdmin(admin.ModelAdmin):
    formfield_overrides = {
        CharField: {'widget': TextInput(attrs={'size': 50})},
        TextField: {'widget': Textarea(attrs={'rows': 5, 'cols': 100})},
    }
    list_display = ['id', 'title', 'description', 'url']
    list_editable = ['title', 'description', 'url']
    search_fields = ['title', 'description', 'url']


# -----------------------------------------------------------------------------


@admin.register(DialoguePacket)
class DialoguePacketAdmin(admin.ModelAdmin):
    form = DialoguePacketAdminForm
    formfield_overrides = {
        CharField: {'widget': TextInput(attrs={'size': 50})},
        TextField: {'widget': Textarea(attrs={'rows': 5, 'cols': 100})},
    }
    list_display = ['id', 'title', 'text']
    list_editable = ['title', 'text']
    search_fields = ['title']


# -----------------------------------------------------------------------------


@admin.register(BiographyPacket)
class BiographyPacketAdmin(admin.ModelAdmin):
    exclude = ['title']
    filter_horizontal = ['acquired_by', 'picture_sets']
    list_display = ['id', 'title', 'text', 'author']
    list_editable = ['title', 'text']
    search_fields = ['title', 'text']
    list_select_related = ['author']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.prefetch_related('acquired_by__user', 'picture_sets__pictures')
        return qs


# -----------------------------------------------------------------------------
    

@admin.register(KnowledgePacket)
class KnowledgePacketAdmin(admin.ModelAdmin):
    filter_horizontal = ['references', 'acquired_by', 'picture_sets', 'skills']
    form = KnowledgePacketAdminForm
    formfield_overrides = {
        CharField: {'widget': TextInput(attrs={'size': 50})},
    }
    # inlines = [CommentInline]
    list_display = ['id', 'title', 'text', 'get_acquired_by']
    list_editable = ['title', 'text']
    list_filter = ['skills__name']
    search_fields = ['title', 'text']
    
    def get_acquired_by(self, obj):
        img_urls = [profile.image.url for profile in obj.acquired_by.all()]
        html = ''
        if img_urls:
            for url in img_urls:
                html += f'<img width="40" height="40" src="{url}">&nbsp;'
        else:
            html = '<h1><font color="red">NIKT</font></h1>'
        return format_html(html)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.prefetch_related('acquired_by')
        return qs
    
        
# -----------------------------------------------------------------------------


@admin.register(MapPacket)
class MapPacketAdmin(admin.ModelAdmin):
    filter_horizontal = ['acquired_by', 'picture_sets']
    form = MapPacketAdminForm
    list_display = ['id', 'title', 'get_acquired_by']
    list_editable = ['title']
    search_fields = ['title']
    
    def get_acquired_by(self, obj):
        img_urls = [profile.image.url for profile in obj.acquired_by.all()]
        html = ''
        if img_urls:
            for url in img_urls:
                html += f'<img width="40" height="40" src="{url}">&nbsp;'
        else:
            html = '<h1><font color="red">NIKT</font></h1>'
        return format_html(html)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.prefetch_related('acquired_by', 'picture_sets')
        return qs
