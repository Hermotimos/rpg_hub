from django.contrib import admin
from rpg_project.utils import formfield_with_cache
from items.models import Item, ItemCollection
from items.admin_filters import OwnerFilter


@admin.register(ItemCollection)
class ItemCollectionAdmin(admin.ModelAdmin):
    list_display = ['id', 'owner', 'name']
    search_fields = ['owner', 'name']
    
    def name_with_owner(self):
        return f"{self.name} [{self.owner.fullname}]"
    
    
@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'collection', 'name', 'info', 'weight', 'is_deleted']
    list_editable = ['collection', 'name', 'info', 'weight', 'is_deleted']
    list_filter = ['is_deleted', OwnerFilter, 'collection']
    search_fields = ['name', 'info']
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        for field in [
            'collection',
        ]:
            if db_field.name == field:
                formfield = formfield_with_cache(field, formfield, request)
        return formfield
