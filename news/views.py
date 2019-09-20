from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from news.models import News, Survey, SurveyOption
from users.models import User, Profile
from news.forms import CreateNewsForm, CreateNewsAnswerForm, CreateSurveyForm, CreateSurveyOptionForm, \
    CreateSurveyAnswerForm, ModifySurveyOptionForm


@login_required
def main_view(request):
    if request.user.profile.character_status == 'gm':
        newss = list(News.objects.all())
        surveys = list(Survey.objects.all())
    else:
        newss = list(request.user.profile.allowed_news.all())
        surveys = list(request.user.profile.surveys_received.all())

    news_with_answers_authors_dict = {n: [a.author for a in n.news_answers.all()] for n in newss}
    surveys_with_answers_authors_dict = {s: [a.author for a in s.survey_answers.all()] for s in surveys}

    context = {
        'page_title': 'Ogłoszenia',
        'newss': newss,
        'surveys': surveys,
        'surveys_with_answers_authors_dict': surveys_with_answers_authors_dict,
        'news_with_answers_authors_dict': news_with_answers_authors_dict
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
            answer = form.save(commit=False)
            answer.news = news
            answer.author = request.user
            form.save()

            subject = f"[RPG] Odpowiedź na ogłoszenie: '{news.title[:30]}...'"
            message = f"{request.user.profile} odpowiedział/a na ogłoszenie '{news.title}':\n" \
                      f"Ogłoszenie: {request.get_host()}/news/detail:{news.id}/\n\n" \
                      f"Odpowiedź: {answer.text}"
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

    profile = request.user.profile
    seen_by = survey.seen_by.all()
    if profile not in seen_by:
        new_seen = profile
        seen_by |= Profile.objects.filter(id=new_seen.id)
        survey.seen_by.set(seen_by)

    survey_options = list(survey.survey_options.all())
    survey_answers = list(survey.survey_answers.all())

    if request.method == 'POST':
        answer_form = CreateSurveyAnswerForm(request.POST, request.FILES)
        option_form = CreateSurveyOptionForm(request.POST)

        if answer_form.is_valid():
            answer = answer_form.save(commit=False)
            answer.survey = survey
            answer.author = request.user
            answer_form.save()

            subject = f"[RPG] Wypowiedż do ankiety: '{survey.title[:30]}...'"
            message = f"{request.user.profile} wypowiedział się co do ankiety '{survey.title}':\n" \
                      f"Ankieta: {request.get_host()}/news/detail:{survey.id}/\n\n" \
                      f"Wypowiedź: {answer.text}"
            sender = settings.EMAIL_HOST_USER
            receivers = []
            for user in User.objects.all():
                if user.profile in survey.addressees.all() and user != request.user:
                    receivers.append(user.email)
            if request.user.profile.character_status != 'gm':
                receivers.append('lukas.kozicki@gmail.com')
            send_mail(subject, message, sender, receivers)

            messages.info(request, f'Twoja odpowiedź została zapisana!')
            return redirect('news:survey-detail', survey_id=survey_id)

        elif option_form.is_valid():
            option = option_form.save(commit=False)
            option.survey = survey
            option.author = request.user
            option_form.save()

            messages.info(request, f'Powiadom uczestników o nowej opcji!')
            return redirect('news:survey-detail', survey_id=survey_id)
    else:
        answer_form = CreateSurveyAnswerForm()
        option_form = CreateSurveyOptionForm()

    context = {
        'page_title': survey.title,
        'survey': survey,
        'survey_options': survey_options,
        'survey_answers': survey_answers,
        'answer_form': answer_form,
        'option_form': option_form
    }
    if request.user.profile in survey.addressees.all() or request.user.profile.character_status == 'gm':
        return render(request, 'news/survey_detail.html', context)
    else:
        return redirect('home:dupa')


@login_required
def vote_yes_view(request, survey_id, option_id):
    option = get_object_or_404(SurveyOption, id=option_id)
    if request.user.profile in option.survey.addressees.all():
        yes_voters = option.yes_voters.all()
        new_yes_voter = request.user.profile
        yes_voters |= Profile.objects.filter(id=new_yes_voter.id)
        option.yes_voters.set(yes_voters)

        if request.user.profile in option.no_voters.all():
            updated_no_voters = option.no_voters.exclude(user=request.user)
            option.no_voters.set(updated_no_voters)

        return redirect('news:survey-detail', survey_id=survey_id)
    else:
        return redirect('home:dupa')


@login_required
def vote_no_view(request, survey_id, option_id):
    option = get_object_or_404(SurveyOption, id=option_id)
    if request.user.profile in option.survey.addressees.all():
        no_voters = option.no_voters.all()
        new_no_voter = request.user.profile
        no_voters |= Profile.objects.filter(id=new_no_voter.id)
        option.no_voters.set(no_voters)

        if request.user.profile in option.yes_voters.all():
            updated_yes_voters = option.yes_voters.exclude(user=request.user)
            option.yes_voters.set(updated_yes_voters)

        return redirect('news:survey-detail', survey_id=survey_id)
    else:
        return redirect('home:dupa')


@login_required
def unvote_view(request, survey_id, option_id):
    option = get_object_or_404(SurveyOption, id=option_id)

    if request.user.profile in option.survey.addressees.all():
        if request.user.profile in option.yes_voters.all():
            updated_yes_voters = option.yes_voters.exclude(user=request.user)
            option.yes_voters.set(updated_yes_voters)
        elif request.user.profile in option.no_voters.all():
            updated_no_voters = option.no_voters.exclude(user=request.user)
            option.no_voters.set(updated_no_voters)

        return redirect('news:survey-detail', survey_id=survey_id)
    else:
        return redirect('home:dupa')


@login_required
def survey_create_view(request):
    if request.method == 'POST':
        form = CreateSurveyForm(authenticated_user=request.user, data=request.POST, files=request.FILES)

        if form.is_valid():
            survey = form.save(commit=False)
            survey.author = request.user
            survey.save()
            addressees = form.cleaned_data['addressees']
            addressees |= Profile.objects.filter(id=request.user.id)
            survey.addressees.set(addressees)

            subject = f"[RPG] Nowa ankieta: '{survey.title[:30]}...'"
            message = f"{request.user.profile} przybił/a coś do słupa ogłoszeń.\n" \
                      f"Podejdź bliżej, aby się przyjrzeć: {request.get_host()}/news/survey_detail:{survey.id}/\n\n" \
                      f"Ogłoszenie: {survey.text}"
            sender = settings.EMAIL_HOST_USER
            receivers = []
            for profile in survey.addressees.all():
                if profile.user != request.user:
                    receivers.append(profile.user.email)
            if request.user.profile.character_status != 'gm':
                receivers.append('lukas.kozicki@gmail.com')
            send_mail(subject, message, sender, receivers)

            messages.info(request, f'Utworzono nową ankietę!')
            return redirect('news:survey-detail', survey_id=survey.id)
    else:
        form = CreateSurveyForm(authenticated_user=request.user)

    context = {
        'page_title': 'Nowa ankieta',
        'form': form,
    }
    return render(request, 'news/survey_create.html', context)


@login_required
def survey_option_modify_view(request, survey_id, option_id):
    option = get_object_or_404(SurveyOption, id=option_id)

    if request.method == 'POST':
        form = ModifySurveyOptionForm(request.POST, instance=option)

        if form.is_valid():
            form.save()
            messages.info(request, f'Zmieniono opcję ankiety!')
            return redirect('news:survey-detail', survey_id=survey_id)
    else:
        form = ModifySurveyOptionForm(instance=option)

    context = {
        'page_title': 'Zmiana opcji ankiety',
        'form': form,
    }
    if request.user == option.author:
        return render(request, 'news/survey_option_modify.html', context)
    else:
        return redirect('home:dupa')


@login_required
def survey_option_delete_view(request, survey_id, option_id):
    option = get_object_or_404(SurveyOption, id=option_id)
    if request.user == option.author:
        option.delete()
        return redirect('news:survey-detail', survey_id=survey_id)
    else:
        return redirect('home:dupa')
