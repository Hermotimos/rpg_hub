from django.contrib import admin
from debates.models import Topic, Debate, Remark


class TopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'date_created')


class DebateAdmin(admin.ModelAdmin):
    list_display = ('name', 'topic', 'is_ended', 'is_individual', 'date_created')


class RemarkAdmin(admin.ModelAdmin):
    list_display = ('text_begin', 'debate', 'author', 'date_posted', 'image')


admin.site.register(Topic, TopicAdmin)
admin.site.register(Debate, DebateAdmin)
admin.site.register(Remark, RemarkAdmin)
