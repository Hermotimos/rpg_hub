from django.contrib import admin
from debates.models import Topic, Debate, Remark


class TopicAdmin(admin.ModelAdmin):
    list_display = ['title', 'date_created']
    search_fields = ['title']


class DebateAdmin(admin.ModelAdmin):
    list_display = ['name', 'topic', 'is_ended', 'is_individual', 'date_created']
    search_fields = ['name']


class RemarkAdmin(admin.ModelAdmin):
    list_display = ['text_begin', 'debate', 'author', 'date_posted', 'image']
    search_fields = ['text']


admin.site.register(Topic, TopicAdmin)
admin.site.register(Debate, DebateAdmin)
admin.site.register(Remark, RemarkAdmin)
