from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from news.models import News
from news.forms import CreateNewsForm


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
    if request.method == 'POST':
        news_form = CreateNewsForm(request.POST or None)
        if news_form.is_valid():
            news = news_form.save(commit=False)
            news.author = request.user
            news = news_form.save()
            return redirect('news-detail', news_slug=news.slug)
    else:
        news_form = CreateNewsForm()

    context = {
        'page_title': 'Nowe ogłoszenie',
        'news_form': news_form
    }
    return render(request, 'news/news-create.html', context)


@login_required
def news_detail_view(request, news_slug):
    queryset = News.objects.get(slug=news_slug)
    page_title = queryset.title[:30] + '...' if len(queryset.title) > 30 else queryset.title

    context = {
        'page_title': page_title,
        'news_details': queryset
    }
    return render(request, 'news/news-detail.html', context)
