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


class SurveyOptionInline(admin.TabularInline):
    model = SurveyOption
    extra = 4


class SurveyAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'text', 'image']
    inlines = [SurveyOptionInline, ]


class SurveyOptionAdmin(admin.ModelAdmin):
    list_display = ['survey', 'author', 'option_text']


admin.site.register(News, NewsAdmin)
admin.site.register(NewsAnswer, NewsAnswerAdmin)
admin.site.register(Survey, SurveyAdmin)
admin.site.register(SurveyOption, SurveyOptionAdmin)
admin.site.register(SurveyAnswer)
