from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from news.models import News
from users.models import User, Profile
from news.forms import CreateNewsForm, CreateResponseForm


@login_required
def news_view(request):
    queryset = News.objects.all()

    context = {
        'page_title': 'Ogłoszenia',
        'queryset': queryset,
    }
    return render(request, 'news/news-main.html', context)


@login_required
def create_news_view(request):
    if request.method == 'POST':
        form = CreateNewsForm(request.POST, request.FILES)
        if form.is_valid():
            news = form.save(commit=False)
            news.author = request.user
            news = form.save()
            news.followers.set(news.allowed_profiles.all())

            subject = f"[RPG] Nowe ogłoszenie: '{news.title[:30]}...'"
            message = f"{request.user.profile} przybił coś do słupa ogłoszeń.\n" \
                      f"Podejdź bliżej, aby się przyjrzeć: {request.get_host()}/news/detail:{news.slug}/\n\n" \
                      f"Ogłoszenie: {news.text}"
            sender = settings.EMAIL_HOST_USER

            receivers_list = []
            for user in User.objects.all():
                if user.profile in news.allowed_profiles.all():
                    receivers_list.append(user.email)
            if request.user.profile.character_status != 'gm':
                receivers_list.append('lukas.kozicki@gmail.com')
            send_mail(subject, message, sender, receivers_list)

            messages.info(request, f'Utworzono nowe ogłoszenie!')
            return redirect('news:detail', news_slug=news.slug)
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

    allowed_str = ', '.join(p.character_name.split(' ', 1)[0] for p in obj.allowed_profiles.all())
    followers_str = ', '.join(p.character_name.split(' ', 1)[0] for p in obj.followers.all())

    if request.method == 'POST':
        form = CreateResponseForm(request.POST, request.FILES)
        if form.is_valid():
            response = form.save(commit=False)
            response.news = obj
            response.author = request.user
            form.save()

            subject = f"[RPG] Odpowiedź na ogłoszenie: '{obj.title[:30]}...'"
            message = f"{request.user.profile} odpowiedział na ogłoszenie '{obj.title}':\n" \
                      f"Ogłoszenie: {request.get_host()}/news/detail:{obj.slug}/\n\n" \
                      f"Odpowiedź: {response.text}"
            sender = settings.EMAIL_HOST_USER

            receivers_list = []
            for user in User.objects.all():
                if user.profile in obj.followers.all():
                    receivers_list.append(user.email)
            if request.user.profile.character_status != 'gm':
                receivers_list.append('lukas.kozicki@gmail.com')
            send_mail(subject, message, sender, receivers_list)

            return redirect('news:detail', news_slug=news_slug)
    else:
        form = CreateResponseForm()

    context = {
        'page_title': obj.title,
        'news': obj,
        'form': form,
        'allowed': allowed_str,
        'followers': followers_str,
    }
    return render(request, 'news/news-detail.html', context)


def unfollow_news_view(request, news_slug):
    obj = News.objects.get(slug=news_slug)
    updated_followers = obj.followers.exclude(user=request.user)
    obj.followers.set(updated_followers)
    messages.info(request, 'Przestałeś obserwować ogłoszenie!')
    return redirect('news:detail', news_slug=news_slug)


def follow_news_view(request, news_slug):
    obj = News.objects.get(slug=news_slug)
    followers = obj.followers.all()
    new_follower = request.user.profile
    followers |= Profile.objects.filter(id=new_follower.id)
    obj.followers.set(followers)
    messages.info(request, 'Obserwujesz ogłoszenie!')
    return redirect('news:detail', news_slug=news_slug)
