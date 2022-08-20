from django import forms
from django.contrib import admin
from django.db import models

from items.admin_filters import OwnerFilter
from items.models import Item, ItemCollection


@admin.register(ItemCollection)
class ItemCollectionAdmin(admin.ModelAdmin):
    list_display = ['id', 'owner', 'name']
    search_fields = ['owner', 'name']
    
    def name_with_owner(self):
        return f"{self.name} [{self.owner.fullname}]"
    
    
@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(attrs={'rows': 2, 'cols': 40})},
        models.CharField: {'widget': forms.TextInput(attrs={'size': 50})},
        models.DecimalField: {'widget': forms.NumberInput(attrs={'size': 15})},
        models.ForeignKey: {'widget': forms.Select(attrs={'style': 'width:180px'})},
    }
    list_display = ['collection', 'name', 'info', 'weight', 'is_deleted']
    list_editable = ['name', 'info', 'weight', 'is_deleted']
    list_filter = ['is_deleted', OwnerFilter]
    search_fields = ['name', 'info']
    list_select_related = ['collection__owner']
    