from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from news.models import News, Survey
from users.models import User, Profile
from news.forms import CreateNewsForm, CreateNewsAnswerForm


@login_required
def main_view(request):
    if request.user.profile.character_status == 'gm':
        newss = list(News.objects.all())
        surveys = list(Survey.objects.all())
    else:
        newss = list(request.user.profile.allowed_news.all())
        surveys = list(request.user.profile.surveys_received.all())

    context = {
        'page_title': 'Ogłoszenia',
        'newss': newss,
        'surveys': surveys
    }
    return render(request, 'news/main.html', context)


@login_required
def create_news_view(request):
    if request.method == 'POST':
        form = CreateNewsForm(authenticated_user=request.user, data=request.POST, files=request.FILES)
        if form.is_valid():
            news = form.save(commit=False)
            news.author = request.user
            news.save()
            allowed_profiles = form.cleaned_data['allowed_profiles']
            allowed_profiles |= Profile.objects.filter(id=request.user.id)
            news.allowed_profiles.set(allowed_profiles)
            news.followers.set(allowed_profiles)

            subject = f"[RPG] Nowe ogłoszenie: '{news.title[:30]}...'"
            message = f"{request.user.profile} przybił/a coś do słupa ogłoszeń.\n" \
                      f"Podejdź bliżej, aby się przyjrzeć: {request.get_host()}/news/detail:{news.id}/\n\n" \
                      f"Ogłoszenie: {news.text}"
            sender = settings.EMAIL_HOST_USER
            receivers = []
            for profile in news.allowed_profiles.all():
                if profile.user != request.user:
                    receivers.append(profile.user.email)
            if request.user.profile.character_status != 'gm':
                receivers.append('lukas.kozicki@gmail.com')
            send_mail(subject, message, sender, receivers)

            messages.info(request, f'Utworzono nowe ogłoszenie!')
            return redirect('news:detail', news_id=news.id)
    else:
        form = CreateNewsForm(authenticated_user=request.user)

    context = {
        'page_title': 'Nowe ogłoszenie',
        'form': form
    }
    return render(request, 'news/create.html', context)


@login_required
def news_detail_view(request, news_id):
    news = get_object_or_404(News, id=news_id)
    news_answers = list(news.news_answers.all())
    allowed_str = ', '.join(p.character_name.split(' ', 1)[0] for p in news.allowed_profiles.all())
    followers_str = ', '.join(p.character_name.split(' ', 1)[0] for p in news.followers.all())

    if request.method == 'POST':
        form = CreateNewsAnswerForm(request.POST, request.FILES)
        if form.is_valid():
            response = form.save(commit=False)
            response.news = news
            response.author = request.user
            form.save()

            subject = f"[RPG] Odpowiedź na ogłoszenie: '{news.title[:30]}...'"
            message = f"{request.user.profile} odpowiedział/a na ogłoszenie '{news.title}':\n" \
                      f"Ogłoszenie: {request.get_host()}/news/detail:{news.id}/\n\n" \
                      f"Odpowiedź: {response.text}"
            sender = settings.EMAIL_HOST_USER
            receivers = []
            for user in User.objects.all():
                if user.profile in news.followers.all() and user != request.user:
                    receivers.append(user.email)
            if request.user.profile.character_status != 'gm':
                receivers.append('lukas.kozicki@gmail.com')
            send_mail(subject, message, sender, receivers)

            messages.info(request, f'Twoja odpowiedź została zapisana!')
            return redirect('news:detail', news_id=news_id)
    else:
        form = CreateNewsAnswerForm()

    context = {
        'page_title': news.title,
        'news': news,
        'news_answers': news_answers,
        'form': form,
        'allowed': allowed_str,
        'followers': followers_str,
    }
    if request.user.profile in news.allowed_profiles.all() or request.user.profile.character_status == 'gm':
        return render(request, 'news/detail.html', context)
    else:
        return redirect('home:dupa')


@login_required
def unfollow_news_view(request, news_id):
    news = get_object_or_404(News, id=news_id)
    if request.user.profile in news.allowed_profiles.all():
        updated_followers = news.followers.exclude(user=request.user)
        news.followers.set(updated_followers)
        messages.info(request, 'Przestałeś obserwować ogłoszenie!')
        return redirect('news:detail', news_id=news_id)
    else:
        return redirect('home:dupa')


@login_required
def follow_news_view(request, news_id):
    news = get_object_or_404(News, id=news_id)
    if request.user.profile in news.allowed_profiles.all():
        followers = news.followers.all()
        new_follower = request.user.profile
        followers |= Profile.objects.filter(id=new_follower.id)
        news.followers.set(followers)
        messages.info(request, 'Obserwujesz ogłoszenie!')
        return redirect('news:detail', news_id=news_id)
    else:
        return redirect('home:dupa')


@login_required
def survey_detail_view(request, survey_id):
    survey = get_object_or_404(Survey, id=survey_id)
    survey_answers = list(survey.survey_answers.all())
    # allowed_str = ', '.join(p.character_name.split(' ', 1)[0] for p in news.allowed_profiles.all())
    # followers_str = ', '.join(p.character_name.split(' ', 1)[0] for p in news.followers.all())

    # if request.method == 'POST':
    #     form = CreateNewsAnswerForm(request.POST, request.FILES)
    #     if form.is_valid():
    #         response = form.save(commit=False)
    #         response.news = news
    #         response.author = request.user
    #         form.save()
    #
    #         subject = f"[RPG] Odpowiedź na ogłoszenie: '{news.title[:30]}...'"
    #         message = f"{request.user.profile} odpowiedział/a na ogłoszenie '{news.title}':\n" \
    #                   f"Ogłoszenie: {request.get_host()}/news/detail:{news.id}/\n\n" \
    #                   f"Odpowiedź: {response.text}"
    #         sender = settings.EMAIL_HOST_USER
    #         receivers = []
    #         for user in User.objects.all():
    #             if user.profile in news.followers.all() and user != request.user:
    #                 receivers.append(user.email)
    #         if request.user.profile.character_status != 'gm':
    #             receivers.append('lukas.kozicki@gmail.com')
    #         send_mail(subject, message, sender, receivers)
    #
    #         messages.info(request, f'Twoja odpowiedź została zapisana!')
    #         return redirect('news:detail', news_id=news_id)
    # else:
    #     form = CreateNewsAnswerForm()

    context = {
        'page_title': survey.title,
        'survey': survey,
        'survey_answers': survey_answers,
        # 'form': form,
        # 'allowed': allowed_str,
        # 'followers': followers_str,
    }
    if request.user.profile in survey.addressees.all() or request.user.profile.character_status == 'gm':
        return render(request, 'news/survey_detail.html', context)
    else:
        return redirect('home:dupa')
