from django.contrib import admin
from contact.models import Demand, Plan, DemandAnswer


class DemandAdmin(admin.ModelAdmin):
    list_display = ['id', 'from_to', 'get_demand_caption', 'is_done']
    search_fields = ['text']

    def from_to(self, obj):
        return str(obj.author) + ' => ' + str(obj.addressee)

    def get_demand_caption(self, obj):
        return obj.text[:100] + '...' if len(str(obj.text)) > 100 else obj.text


class DemandAnswerAdmin(admin.ModelAdmin):
    list_display = ['get_demand_info', 'demand', 'id', 'get_answer_caption', ]
    search_fields = ['text']

    def get_demand_info(self, obj):
        return f'{obj.demand.id} [{str(obj.demand.author)} => {str(obj.demand.addressee)}]'

    def get_answer_caption(self, obj):
        return obj.text[:100] + '...' if len(str(obj.text)) > 100 else obj.text


class PlanAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'inform_gm', 'get_plan_caption']
    search_fields = ['text']

    def get_plan_caption(self, obj):
        return obj.text[:100] + '...' if len(str(obj.text)) > 100 else obj.text


admin.site.register(Demand, DemandAdmin)
admin.site.register(Plan, PlanAdmin)
admin.site.register(DemandAnswer, DemandAnswerAdmin)
