from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Max
from news.models import News
from users.models import User
from news.forms import CreateNewsForm, CreateResponseForm


@login_required
def news_view(request):
    news_list = News.objects.all()

    news_with_last_activity_dict = {news: news.responses.all().aggregate(Max('date_posted'))['date_posted__max']
                                       for news in news_list}

    context = {
        'page_title': 'Słup ogłoszeń',
        'news_list': news_list,
        'news_with_last_activity_dict': news_with_last_activity_dict
    }
    return render(request, 'news/news-list.html', context)


@login_required
def create_news_view(request):
    if request.method == 'POST':
        news_form = CreateNewsForm(request.POST, request.FILES)
        if news_form.is_valid():
            news = news_form.save(commit=False)
            news.author = request.user
            news = news_form.save()

            subject = f"[RPG] Nowe ogłoszenie: {news.title[:30]}..."
            message = f"{request.user.profile} przybił coś do słupa ogłoszeń.\n" \
                      f"Podejdź bliżej, aby zobaczyć: http://127.0.0.1:8000/news/{news.slug}/"
            sender = settings.EMAIL_HOST_USER
            receivers_list = []
            for user in User.objects.all():
                if user.profile in news.allowed_profiles.all():
                    receivers_list.append(user.email)
            if request.user.profile.character_status != 'gm':
                receivers_list.append('lukas.kozicki@gmail.com')
            send_mail(subject, message, sender, receivers_list)

            messages.success(request, f'Utworzono nowe ogłoszenie!')
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

    if request.method == 'POST':
        response_form = CreateResponseForm(request.POST, request.FILES)
        if response_form.is_valid():
            response = response_form.save(commit=False)
            response.news = queryset
            response.author = request.user
            response_form.save()
            return redirect('news-detail', news_slug=news_slug)
    else:
        response_form = CreateResponseForm()

    context = {
        'page_title': page_title,
        'news_details': queryset,
        'response_form': response_form
    }
    return render(request, 'news/news-detail.html', context)
