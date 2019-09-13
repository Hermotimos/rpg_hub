from django.contrib import admin
from contact.models import Demand, Plan


class DemandAdmin(admin.ModelAdmin):
    list_display = ['id', 'from_to', 'get_caption', 'is_done']

    def from_to(self, obj):
        return str(obj.author) + ' => ' + str(obj.addressee)

    def get_caption(self, obj):
        return obj.text[:100] + '...' if len(str(obj.text)) > 100 else obj.text


class PlanAdmin(admin.ModelAdmin):
    list_display = ['id', 'inform_gm', 'author', 'get_caption']

    def get_caption(self, obj):
        return obj.text[:100] + '...' if len(str(obj.text)) > 100 else obj.text


admin.site.register(Demand, DemandAdmin)
admin.site.register(Plan, PlanAdmin)
