from django.contrib import admin
from items.admin_filters import CollectionFilter
from rpg_project.utils import formfield_with_cache
from items.models import Collection, Item


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'type', 'owner']
    list_editable = ['name', 'type', 'owner']
    list_filter = [CollectionFilter]
    search_fields = ['name']
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):

        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        for field in [
            'owner',
        ]:
            if db_field.name == field:
                formfield = formfield_with_cache(field, formfield, request)
        return formfield

    
@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'collection', 'name', 'weight']
    list_editable = ['collection', 'name', 'weight']
    list_filter = ['collection__owner']
    search_fields = ['name']
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        for field in [
            'collection',
        ]:
            if db_field.name == field:
                formfield = formfield_with_cache(field, formfield, request)
        return formfield
