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


def news_detail_view(request, slug):
    news_details = News.objects.filter(slug=slug)

    context = {
        'page_title': news_details.title[:30],
        'news_details': news_details
    }
    return render(request, 'news/news-detail', context)
