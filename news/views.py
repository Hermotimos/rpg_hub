from django.shortcuts import render


# Create your views here.
def news_view(request):
    context = {
        'page_title': 'Słup ogłoszeń'
    }
    return render(request, 'news/news-list.html', context)


def create_news_view(request):
    context = {
        'page_title': 'Nowe ogłoszenie'
    }
    return render(request, 'news/news-create.html', context)
