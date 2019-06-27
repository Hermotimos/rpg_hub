from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import News


@login_required
def news_view(request):
    queryset = News.objects.all()

    context = {
        'page_title': 'Słup ogłoszeń',
        'news_list': queryset,
    }
    return render(request, 'news/news-list.html', context)


@login_required
def create_news_view(request):
    context = {
        'page_title': 'Nowe ogłoszenie'
    }
    return render(request, 'news/news-create.html', context)


@login_required
def news_detail_view(request, slug):
    queryset = News.objects.get(slug=slug)
    page_title = queryset.title[:30] + '...' if len(queryset.title) > 30 else queryset.title

    context = {
        'page_title': page_title,
        'news_details': queryset
    }
    return render(request, 'news/news-detail.html', context)
