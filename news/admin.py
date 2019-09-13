from django.contrib import admin
from .models import News, NewsAnswer, Survey, SurveyOption, SurveyAnswer


class NewsAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'title', 'date_posted', 'image']
    list_editable = ['title', 'image']


class NewsAnswerAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_news', 'author', 'get_caption', 'date_posted']

    def get_news(self, obj):
        return obj.news.title

    def get_caption(self, obj):
        return obj.text[:100] + '...' if len(str(obj.text)) > 100 else obj.text


admin.site.register(News, NewsAdmin)
admin.site.register(NewsAnswer, NewsAnswerAdmin)
admin.site.register(Survey)
admin.site.register(SurveyOption)
admin.site.register(SurveyAnswer)
