from django.shortcuts import render


# Create your views here.
def news_view(request):
    context = {
        'page_title': 'Słup ogłoszeń'
    }
    return render(request, 'news/news-list.html', context)
