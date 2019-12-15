from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db.models import Max, Min, Prefetch, Q
from django.shortcuts import render, redirect, get_object_or_404

from news.models import News, Survey, SurveyOption
from rpg_project.utils import query_debugger
from users.models import User, Profile
from news.forms import CreateNewsForm, CreateNewsAnswerForm, CreateSurveyForm, CreateSurveyOptionForm, \
    CreateSurveyAnswerForm, ModifySurveyOptionForm


@query_debugger
@login_required
def main_view(request):
    profile = request.user.profile
    if profile.character_status == 'gm':
        newss = News.objects.all()
        surveys = Survey.objects.all()
    else:
        newss = profile.allowed_news.all()
        surveys = profile.surveys_received.all()\

    newss = newss.annotate(last_news_answer=Max('news_answers__date_posted'))\
        .select_related('author__profile') \
        .prefetch_related('news_answers__author__profile')

    surveys = surveys\
        .select_related('author__profile')\
        .prefetch_related('survey_answers__author__profile')

    context = {
        'page_title': 'Ogłoszenia',
        'newss': newss,
        'surveys': surveys,
    }
    return render(request, 'news/main.html', context)


@query_debugger
@login_required
def create_news_view(request):
    profile = request.user.profile
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
            message = f"{profile} przybił/a coś do słupa ogłoszeń.\n" \
                      f"Podejdź bliżej, aby się przyjrzeć: {request.get_host()}/news/news-detail:{news.id}/\n\n" \
                      f"Ogłoszenie: {news.text}"
            sender = settings.EMAIL_HOST_USER
            receivers = []
            for profile in news.allowed_profiles.all():
                if profile.user != request.user:
                    receivers.append(profile.user.email)
            if profile.character_status != 'gm':
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
    return render(request, 'news/news_create.html', context)


@query_debugger
@login_required
def news_detail_view(request, news_id):
    profile = request.user.profile
    news = get_object_or_404(News, id=news_id)

    news_allowed_profiles = news.allowed_profiles.all()
    news_followers = news.followers.all()

    news_seen_by = news.seen_by.all()
    if profile not in news_seen_by:
        news.seen_by.add(profile)

    answers = []
    last_answer_seen_by_imgs = []
    if news.news_answers.all():
        answers = news.news_answers.all().select_related('author__profile')
        last_answer = news.news_answers.order_by('-date_posted')[0]
        if profile not in last_answer.seen_by.all():
            last_answer.seen_by.add(profile)
        last_answer_seen_by_imgs = (p.image for p in last_answer.seen_by.all())

    if request.method == 'POST':
        form = CreateNewsAnswerForm(request.POST, request.FILES)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.news = news
            answer.author = request.user
            form.save()

            subject = f"[RPG] Odpowiedź na ogłoszenie: '{news.title[:30]}...'"
            message = f"{profile} odpowiedział/a na ogłoszenie '{news.title}':\n" \
                      f"Ogłoszenie: {request.get_host()}/news/news-detail:{news.id}/\n\n" \
                      f"Odpowiedź: {answer.text}"
            sender = settings.EMAIL_HOST_USER
            receivers = []
            for user in User.objects.all():
                if user.profile in news_followers and user != request.user:
                    receivers.append(user.email)
            if profile.character_status != 'gm':
                receivers.append('lukas.kozicki@gmail.com')
            send_mail(subject, message, sender, receivers)

            messages.info(request, f'Twoja odpowiedź została zapisana!')
            return redirect('news:detail', news_id=news_id)
    else:
        form = CreateNewsAnswerForm()

    context = {
        'page_title': news.title,
        'news': news,
        'answers': answers,
        'news_seen_by': news_seen_by,
        'last_answer_seen_by_imgs': last_answer_seen_by_imgs,
        'form': form,
        'news_allowed_profiles': news_allowed_profiles,
        'news_followers': news_followers,
    }
    if profile in news.allowed_profiles.all() or profile.character_status == 'gm':
        return render(request, 'news/news_detail.html', context)
    else:
        return redirect('home:dupa')


@query_debugger
@login_required
def unfollow_news_view(request, news_id):
    profile = request.user.profile
    news = get_object_or_404(News, id=news_id)
    if profile in news.allowed_profiles.all():
        # TODO: remove the above if news.followers.remove(profile) works
        # updated_followers = news.followers.exclude(user=request.user)
        news.followers.remove(profile)
        messages.info(request, 'Przestałeś obserwować ogłoszenie!')
        return redirect('news:detail', news_id=news_id)
    else:
        return redirect('home:dupa')


@query_debugger
@login_required
def follow_news_view(request, news_id):
    profile = request.user.profile
    news = get_object_or_404(News, id=news_id)
    if profile in news.allowed_profiles.all():
        # TODO: remove the above if news.followers.add(profile) works
        # followers = news.followers.all()
        # new_follower = profile
        # followers |= Profile.objects.filter(id=new_follower.id)
        news.followers.add(profile)
        messages.info(request, 'Obserwujesz ogłoszenie!')
        return redirect('news:detail', news_id=news_id)
    else:
        return redirect('home:dupa')


@query_debugger
@login_required
def survey_detail_view(request, survey_id):
    profile = request.user.profile
    survey = get_object_or_404(Survey, id=survey_id)

    survey_seen_by = survey.seen_by.all()
    if profile not in survey_seen_by:
        survey.seen_by.add(profile)

    options = survey.survey_options.all()\
        .prefetch_related('yes_voters', 'no_voters')\
        .select_related('author__profile')
    answers = survey.survey_answers.all().select_related('author__profile')

    last_answer_seen_by_imgs = []
    if answers:
        last_answer = answers.order_by('-date_posted')[0]
        if profile not in last_answer.seen_by.all():
            last_answer.seen_by.add(profile)
        last_answer_seen_by_imgs = (p.image for p in last_answer.seen_by.all())

    if request.method == 'POST':
        answer_form = CreateSurveyAnswerForm(request.POST, request.FILES)
        option_form = CreateSurveyOptionForm(request.POST)

        if answer_form.is_valid():
            answer = answer_form.save(commit=False)
            answer.survey = survey
            answer.author = request.user
            answer_form.save()

            subject = f"[RPG] Wypowiedż do ankiety: '{survey.title[:30]}...'"
            message = f"{profile} wypowiedział się co do ankiety '{survey.title}':\n" \
                      f"Ankieta: {request.get_host()}/news/survey-detail:{survey.id}/\n\n" \
                      f"Wypowiedź: {answer.text}"
            sender = settings.EMAIL_HOST_USER
            receivers = []
            for user in User.objects.all():
                if user.profile in survey.addressees.all() and user != request.user:
                    receivers.append(user.email)
            if profile.character_status != 'gm':
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
        'options': options,
        'answers': answers,
        'survey_seen_by': survey_seen_by,
        'last_answer_seen_by_imgs': last_answer_seen_by_imgs,
        'answer_form': answer_form,
        'option_form': option_form
    }
    if profile in survey.addressees.all() or profile.character_status == 'gm':
        return render(request, 'news/survey_detail.html', context)
    else:
        return redirect('home:dupa')


@query_debugger
@login_required
def vote_yes_view(request, survey_id, option_id):
    profile = request.user.profile
    option = get_object_or_404(SurveyOption, id=option_id)
    if profile in option.survey.addressees.all():
        # yes_voters = option.yes_voters.all()
        # new_yes_voter = profile
        # yes_voters |= Profile.objects.filter(id=new_yes_voter.id)
        # option.yes_voters.set(yes_voters)
        option.yes_voters.add(profile)

        if profile in option.no_voters.all():
            # updated_no_voters = option.no_voters.exclude(user=request.user)
            # option.no_voters.set(updated_no_voters)
            option.no_voters.remove(profile)

        messages.info(request, 'Twój głos został dodany!')
        return redirect('news:survey-detail', survey_id=survey_id)
    else:
        return redirect('home:dupa')


@query_debugger
@login_required
def vote_no_view(request, survey_id, option_id):
    profile = request.user.profile
    option = get_object_or_404(SurveyOption, id=option_id)
    if profile in option.survey.addressees.all():
        # no_voters = option.no_voters.all()
        # new_no_voter = profile
        # no_voters |= Profile.objects.filter(id=new_no_voter.id)
        # option.no_voters.set(no_voters)
        option.no_voters.add(profile)

        if profile in option.yes_voters.all():
            # updated_yes_voters = option.yes_voters.exclude(user=request.user)
            # option.yes_voters.set(updated_yes_voters)
            option.yes_voters.remove(profile)

        messages.info(request, 'Twój głos został dodany!')
        return redirect('news:survey-detail', survey_id=survey_id)
    else:
        return redirect('home:dupa')


@query_debugger
@login_required
def unvote_view(request, survey_id, option_id):
    profile = request.user.profile
    option = get_object_or_404(SurveyOption, id=option_id)

    if profile in option.survey.addressees.all():
        if profile in option.yes_voters.all():
            # updated_yes_voters = option.yes_voters.exclude(user=request.user)
            # option.yes_voters.set(updated_yes_voters)
            option.yes_voters.remove(profile)
        elif profile in option.no_voters.all():
            # updated_no_voters = option.no_voters.exclude(user=request.user)
            # option.no_voters.set(updated_no_voters)
            option.no_voters.remove(profile)

        messages.info(request, 'Twój głos został skasowany!')
        return redirect('news:survey-detail', survey_id=survey_id)
    else:
        return redirect('home:dupa')


@query_debugger
@login_required
def survey_create_view(request):
    profile = request.user.profile
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
            message = f"{profile} przybił/a coś do słupa ogłoszeń.\n" \
                      f"Podejdź bliżej, aby się przyjrzeć: {request.get_host()}/news/survey-detail:{survey.id}/\n\n" \
                      f"Ogłoszenie: {survey.text}"
            sender = settings.EMAIL_HOST_USER
            receivers = []
            for profile in survey.addressees.all():
                if profile.user != request.user:
                    receivers.append(profile.user.email)
            if profile.character_status != 'gm':
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


@query_debugger
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


@query_debugger
@login_required
def survey_option_delete_view(request, survey_id, option_id):
    option = get_object_or_404(SurveyOption, id=option_id)
    if request.user == option.author:
        option.delete()
        return redirect('news:survey-detail', survey_id=survey_id)
    else:
        return redirect('home:dupa')
