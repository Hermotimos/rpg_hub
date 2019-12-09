from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
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
        newss = News.objects.all().select_related('author__profile').prefetch_related('news_answers__author__profile')
        surveys = Survey.objects.all().select_related('author__profile').prefetch_related('survey_answers__author__profile')
    else:
        newss = profile.allowed_news.all().select_related('author__profile').prefetch_related('news_answers__author__profile')
        surveys = profile.surveys_received.all().select_related('author__profile').prefetch_related('survey_answers__author__profile')

    # news_with_answers_authors_dict = {
    #     n: [
    #         a.author for a in n.news_answers.all().select_related('author')
    #     ] for n in newss
    # }
    # surveys_with_answers_authors_dict = {
    #     s: [
    #         a.author for a in s.survey_answers.all().select_related('author')
    #     ] for s in surveys
    # }

    context = {
        'page_title': 'Ogłoszenia',
        'newss': newss,
        'surveys': surveys,
        # 'surveys_with_answers_authors_dict': surveys_with_answers_authors_dict,
        # 'news_with_answers_authors_dict': news_with_answers_authors_dict
    }
    return render(request, 'news/main.html', context)


@query_debugger
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
                      f"Podejdź bliżej, aby się przyjrzeć: {request.get_host()}/news/news-detail:{news.id}/\n\n" \
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
    return render(request, 'news/news_create.html', context)


@query_debugger
@login_required
def news_detail_view(request, news_id):
    news = get_object_or_404(News, id=news_id)

    if request.user.profile not in news.seen_by.all():
        news.seen_by.add(request.user.profile)

    last_news_answer = news.last_news_answer()
    last_news_answer_seen_by_imgs = ()
    if last_news_answer:
        if request.user.profile not in last_news_answer.seen_by.all():
            last_news_answer.seen_by.add(request.user.profile)
        last_news_answer_seen_by_imgs = (p.image for p in last_news_answer.seen_by.all())

    news_answers = news.news_answers.all().select_related('author')
    allowed_imgs = [p.image for p in news.allowed_profiles.all()]
    followers_imgs = [p.image for p in news.followers.all()]

    if request.method == 'POST':
        form = CreateNewsAnswerForm(request.POST, request.FILES)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.news = news
            answer.author = request.user
            form.save()

            subject = f"[RPG] Odpowiedź na ogłoszenie: '{news.title[:30]}...'"
            message = f"{request.user.profile} odpowiedział/a na ogłoszenie '{news.title}':\n" \
                      f"Ogłoszenie: {request.get_host()}/news/news-detail:{news.id}/\n\n" \
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
        'last_news_answer_seen_by_imgs': last_news_answer_seen_by_imgs,
        'form': form,
        'allowed_imgs': allowed_imgs,
        'followers_imgs': followers_imgs,
    }
    if request.user.profile in news.allowed_profiles.all() or request.user.profile.character_status == 'gm':
        return render(request, 'news/news_detail.html', context)
    else:
        return redirect('home:dupa')


@query_debugger
@login_required
def unfollow_news_view(request, news_id):
    news = get_object_or_404(News, id=news_id)
    if request.user.profile in news.allowed_profiles.all():
        # TODO: remove the above if news.followers.remove(request.user.profile) works
        # updated_followers = news.followers.exclude(user=request.user)
        news.followers.remove(request.user.profile)
        messages.info(request, 'Przestałeś obserwować ogłoszenie!')
        return redirect('news:detail', news_id=news_id)
    else:
        return redirect('home:dupa')


@query_debugger
@login_required
def follow_news_view(request, news_id):
    news = get_object_or_404(News, id=news_id)
    if request.user.profile in news.allowed_profiles.all():
        # TODO: remove the above if news.followers.add(request.user.profile) works
        # followers = news.followers.all()
        # new_follower = request.user.profile
        # followers |= Profile.objects.filter(id=new_follower.id)
        news.followers.add(request.user.profile)
        messages.info(request, 'Obserwujesz ogłoszenie!')
        return redirect('news:detail', news_id=news_id)
    else:
        return redirect('home:dupa')


@query_debugger
@login_required
def survey_detail_view(request, survey_id):
    survey = get_object_or_404(Survey, id=survey_id)

    if request.user.profile not in survey.seen_by.all():
        survey.seen_by.add(request.user.profile)

    last_survey_answer = survey.last_survey_answer()
    last_survey_answer_seen_by_imgs = ()
    if last_survey_answer:
        if request.user.profile not in last_survey_answer.seen_by.all():
            last_survey_answer.seen_by.add(request.user.profile)
        last_survey_answer_seen_by_imgs = (p.image for p in last_survey_answer.seen_by.all())

    survey_options = survey.survey_options.all().prefetch_related('yes_voters', 'no_voters')
    survey_answers = survey.survey_answers.all().select_related('author')

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
                      f"Ankieta: {request.get_host()}/news/survey-detail:{survey.id}/\n\n" \
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
        'last_survey_answer_seen_by_imgs': last_survey_answer_seen_by_imgs,
        'answer_form': answer_form,
        'option_form': option_form
    }
    if request.user.profile in survey.addressees.all() or request.user.profile.character_status == 'gm':
        return render(request, 'news/survey_detail.html', context)
    else:
        return redirect('home:dupa')


@query_debugger
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


@query_debugger
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


@query_debugger
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


@query_debugger
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
                      f"Podejdź bliżej, aby się przyjrzeć: {request.get_host()}/news/survey-detail:{survey.id}/\n\n" \
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
