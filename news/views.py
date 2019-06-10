from django.shortcuts import render
from .models import News


def news_view(request):
    news_list = News.objects.all()

    context = {
        'page_title': 'Słup ogłoszeń',
        'news_list': news_list,
    }
    return render(request, 'news/news-list.html', context)


def create_news_view(request):
    context = {
        'page_title': 'Nowe ogłoszenie'
    }
    return render(request, 'news/news-create.html', context)
