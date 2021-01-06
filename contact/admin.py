from django.contrib import admin
from django.utils.html import format_html

from contact.models import Demand, Plan, DemandAnswer


class DemandAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'from_to', 'demand_caption', 'is_done']
    list_select_related = ['author', 'addressee']
    search_fields = ['text']

    def demand_caption(self, obj):
        text = obj.text
        return text[:100] + '...' if len(str(text)) > 100 else text
    
    def from_to(self, obj):
        author_img = obj.author.image.url
        addressee_img = obj.addressee.image.url
    
        if author_img:
            author_img = f'<img width="40" height="40" ' \
                         f'src="{author_img}">'
        else:
            author_img = '<img width="40" height="40" ' \
                         'src="media/profile_pics/profile_default.jpg">'
    
        if addressee_img:
            addressee_img = f'<img width="40" height="40" ' \
                            f'src="{addressee_img}">'
        else:
            addressee_img = '<img width="40" height="40" ' \
                            'src="media/profile_pics/profile_default.jpg">'
    
        return format_html(author_img + ' ☛ ' + addressee_img)


class DemandAnswerAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_demand_info', 'get_answer_caption']
    list_select_related = ['demand__author', 'demand__addressee']
    ordering = ['-date_posted']
    search_fields = ['text']

    def get_answer_caption(self, obj):
        text = obj.text
        return text[:100] + '...' if len(str(text)) > 100 else text

    def get_demand_info(self, obj):
        return format_html(f'Dezyderat nr {obj.demand.id}'
                           f'<br>[{str(obj.demand.author)} '
                           f'=> {str(obj.demand.addressee)}]'
                           f'<br><b>{obj.demand}</b>')


class PlanAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'inform_gm', 'get_plan_caption']
    list_select_related = ['author']
    search_fields = ['text']

    def get_plan_caption(self, obj):
        text = obj.text
        if obj.author.status == 'gm' or obj.inform_gm:
            return text[:100] + '...' if len(str(text)) > 100 else text
        else:
            return format_html('<b><font color="red">TOP SECRET</font></b>')


admin.site.register(Demand, DemandAdmin)
admin.site.register(Plan, PlanAdmin)
admin.site.register(DemandAnswer, DemandAnswerAdmin)
