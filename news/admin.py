from django.contrib import admin
from .models import News, NewsAnswer


class NewsAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'title', 'date_posted', 'image']
    list_editable = ['title', 'image']


class NewsAnswerAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_news', 'author', 'get_caption', 'date_posted']

    def get_news(self, obj):
        return obj.news.title

    def get_caption(self, obj):
        return obj.text[:100] + '...'


admin.site.register(News, NewsAdmin)
admin.site.register(NewsAnswer, NewsAnswerAdmin)
