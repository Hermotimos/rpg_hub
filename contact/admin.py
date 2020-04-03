from django.contrib import admin
from django.utils.html import format_html

from contact.models import Demand, Plan, DemandAnswer


class DemandAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'from_to', 'demand_caption', 'is_done']
    search_fields = ['text']

    def demand_caption(self, obj):
        text = obj.text
        return text[:100] + '...' if len(str(text)) > 100 else text
    
    def from_to(self, obj):
        return str(obj.author) + ' => ' + str(obj.addressee)


class DemandAnswerAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_demand_info', 'get_answer_caption']
    search_fields = ['text']

    def get_demand_info(self, obj):
        return format_html(f'Dezyderat nr {obj.demand.id}'
                           f'<br>[{str(obj.demand.author)} '
                           f'=> {str(obj.demand.addressee)}]'
                           f'<br><b>{obj.demand}</b>')

    def get_answer_caption(self, obj):
        text = obj.text
        return text[:100] + '...' if len(str(text)) > 100 else text


class PlanAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'inform_gm', 'get_plan_caption']
    search_fields = ['text']

    def get_plan_caption(self, obj):
        text = obj.text
        if obj.author.profile.status == 'gm' or obj.inform_gm:
            return text[:100] + '...' if len(str(text)) > 100 else text
        else:
            return format_html('<b><font color="red">TOP SECRET</font></b>')


admin.site.register(Demand, DemandAdmin)
admin.site.register(Plan, PlanAdmin)
admin.site.register(DemandAnswer, DemandAnswerAdmin)
