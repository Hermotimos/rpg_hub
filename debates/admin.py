from django.contrib import admin
from debates.models import Topic, Debate, Remark


class TopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'date_created', 'date_updated')


admin.site.register(Topic, TopicAdmin)


class DebateAdmin(admin.ModelAdmin):
    list_display = ('title', 'topic', 'is_ended', 'is_individual', 'date_created', 'date_updated', )


admin.site.register(Debate, DebateAdmin)
admin.site.register(Remark)
