from django.contrib import admin
from rpg_project.utils import formfield_with_cache
from items.models import Item
from items.admin_filters import OwnerFilter


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'owner', 'type', 'name', 'info', 'weight']
    list_editable = ['owner', 'type', 'name', 'info', 'weight']
    list_filter = [OwnerFilter, 'type']
    search_fields = ['name', 'info']
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        for field in [
            'owner',
        ]:
            if db_field.name == field:
                formfield = formfield_with_cache(field, formfield, request)
        return formfield
