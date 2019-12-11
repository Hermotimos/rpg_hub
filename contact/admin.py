from contact.models import Demand, Plan, DemandAnswer
from django.contrib import admin
from django.utils.html import format_html


class DemandAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'author_to_addressee', 'demand_caption', 'is_done']
    search_fields = ['text']

    def author_to_addressee(self, obj):
        return str(obj.author) + ' => ' + str(obj.addressee)

    def demand_caption(self, obj):
        return obj.text[:100] + '...' if len(str(obj.text)) > 100 else obj.text


class DemandAnswerAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_demand_info', 'get_answer_caption']
    search_fields = ['text']

    def get_demand_info(self, obj):
        return format_html(f'Dezyderat nr {obj.demand.id}'
                           f'<br>[{str(obj.demand.author)} => {str(obj.demand.addressee)}]'
                           f'<br><b>{obj.demand}</b>')

    def get_answer_caption(self, obj):
        return obj.text[:100] + '...' if len(str(obj.text)) > 100 else obj.text


class PlanAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'inform_gm', 'get_plan_caption']
    search_fields = ['text']

    def get_plan_caption(self, obj):
        if obj.author.profile.character_status == 'gm' or obj.inform_gm:
            return obj.text[:100] + '...' if len(str(obj.text)) > 100 else obj.text
        else:
            return format_html('<b><font color="red">TOP SECRET</font></b>')


admin.site.register(Demand, DemandAdmin)
admin.site.register(Plan, PlanAdmin)
admin.site.register(DemandAnswer, DemandAnswerAdmin)
