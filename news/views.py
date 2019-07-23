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
    queryset = News.objects.all()

    news_with_last_activity_dict = {news: news.responses.all().aggregate(Max('date_posted'))['date_posted__max']
                                    for news in queryset}

    context = {
        'page_title': 'Słup ogłoszeń',
        'queryset': queryset,
        'news_with_last_activity_dict': news_with_last_activity_dict
    }
    return render(request, 'news/news-list.html', context)


@login_required
def create_news_view(request):
    if request.method == 'POST':
        form = CreateNewsForm(request.POST, request.FILES)
        if form.is_valid():
            news = form.save(commit=False)
            news.author = request.user
            news = form.save()

            subject = f"[RPG] Nowe ogłoszenie: {news.title[:30]}..."
            message = f"{request.user.profile} przybił coś do słupa ogłoszeń.\n" \
                      f"Podejdź bliżej, aby zobaczyć: {request.get_host()}/news/{news.slug}/"
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
        form = CreateNewsForm()

    context = {
        'page_title': 'Nowe ogłoszenie',
        'form': form
    }
    return render(request, 'news/news-create.html', context)


@login_required
def news_detail_view(request, news_slug):
    obj = News.objects.get(slug=news_slug)

    page_title = obj.title[:30] + '...' if len(obj.title) > 30 else obj.title
    allowed = ', '.join(p.character_name.split(' ', 1)[0]
                        for p in obj.allowed_profiles.all()
                        if p.character_status != 'gm')

    if request.method == 'POST':
        form = CreateResponseForm(request.POST, request.FILES)
        if form.is_valid():
            response = form.save(commit=False)
            response.news = obj
            response.author = request.user
            form.save()
            return redirect('news-detail', news_slug=news_slug)
    else:
        form = CreateResponseForm()

    context = {
        'page_title': page_title,
        'news': obj,
        'form': form,
        'allowed': allowed
    }
    return render(request, 'news/news-detail.html', context)
