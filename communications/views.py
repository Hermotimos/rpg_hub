from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db.models import Prefetch
from django.shortcuts import render, redirect, get_object_or_404

from news.forms import (CreateNewsForm, CreateTopicForm, CreateNewsAnswerForm,
                        CreateSurveyOptionForm, ModifySurveyOptionForm)
from communications.models import Topic, Thread, Debate, Announcement, Statement
from users.models import Profile


@login_required
def announcements_view(request):
    profile = request.user.profile
    
    if profile.status == 'gm':
        announcements = Announcement.objects.all()
    else:
        announcements = Announcement.objects.filter(known_directly=profile)

    announcements = announcements.prefetch_related(
        'statements__author', 'statements__seen_by')
    announcements = announcements.order_by('-created_at')
    
    topics = Topic.objects.filter(threads__in=announcements)
    topics = topics.prefetch_related(
        Prefetch('threads', queryset=announcements))
    topics = topics.distinct()

    context = {
        'page_title': 'Ogłoszenia',
        'topics': topics,
        # 'unseen_news': profile.unseen_news,
    }
    return render(request, 'communications/announcements.html', context)


# TODO 1 create topic form and view with parameter for Thread kind,
#     to then redirect to the proper Thread kind create form

# @login_required
# def create_topic_view(request):
#     form = CreateTopicForm(request.POST or None)
#     if form.is_valid():
#         topic = form.save()
#         messages.info(
#             request, f"Utworzono nowy temat ogłoszeń: '{topic.title}'!")
#         return redirect('news:main')
#
#     context = {
#         'page_title': "Nowy temat ogłoszeń",
#         'form_1': form,
#     }
#     return render(request, '_create_form.html', context)
#
#
# @login_required
# def create_news_view(request):
#     profile = request.user.profile
#
#     news_form = CreateNewsForm(data=request.POST or None,
#                                files=request.FILES or None,
#                                authenticated_user=request.user)
#     news_answer_form = CreateNewsAnswerForm(
#         data=request.POST or None, files=request.FILES or None)
#
#     if news_form.is_valid() and news_answer_form.is_valid():
#         news = news_form.save(commit=False)
#         news.author = request.user.profile
#         news.save()
#         allowed_profiles = news_form.cleaned_data['allowed_profiles']
#         allowed_profiles |= Profile.objects.filter(id=request.user.id)
#         news.allowed_profiles.set(allowed_profiles)
#         news.followers.set(allowed_profiles)
#
#         answer = news_answer_form.save(commit=False)
#         answer.news = news
#         answer.author = request.user.profile
#         news_answer_form.save()
#
#         subject = f"[RPG] Nowe ogłoszenie: '{news.title[:30]}...'"
#         message = f"{profile} przybił/a coś do słupa ogłoszeń.\n" \
#                   f"Podejdź bliżej, aby się przyjrzeć: {request.get_host()}/news/news-detail:{news.id}/\n\n"
#         sender = settings.EMAIL_HOST_USER
#         receivers = []
#         for profile in news.allowed_profiles.all():
#             if profile.user != request.user:
#                 receivers.append(profile.user.email)
#         if profile.status != 'gm':
#             receivers.append("lukas.kozicki@gmail.com")
#         send_mail(subject, message, sender, receivers)
#
#         messages.info(request, f"Utworzono nowe ogłoszenie!")
#         return redirect('news:detail', news_id=news.id)
#
#     context = {
#         'page_title': "Nowe ogłoszenie",
#         'form_1': news_form,
#         'form_2': news_answer_form,
#     }
#     return render(request, '_create_form.html', context)


@login_required
def announcement_view(request, announcement_id):
    profile = request.user.profile
    announcement = Announcement.objects.prefetch_related(
        'statements__seen_by', 'statements__author', 'followers',
        'known_directly')
    announcement = announcement.get(id=announcement_id)

    # Update all statements to be seen by the profile
    SeenBy = Statement.seen_by.through
    relations = []
    for statement in announcement.statements.all():
        relations.append(
            SeenBy(statement_id=statement.id, profile_id=profile.id))
    SeenBy.objects.bulk_create(relations, ignore_conflicts=True)

    # if request.method == 'POST':
    #     form = CreateNewsAnswerForm(request.POST, request.FILES)
    #     if form.is_valid():
    #         answer = form.save(commit=False)
    #         answer.news = news
    #         answer.author = request.user.profile
    #         form.save()
    #
    #         subject = f"[RPG] Odpowiedź na ogłoszenie: '{news.title[:30]}...'"
    #         message = f"{profile} odpowiedział/a na ogłoszenie '{news.title}':\n" \
    #                   f"Ogłoszenie: {request.get_host()}/news/news-detail:{news.id}/\n\n" \
    #                   f"Odpowiedź:\n{answer.text}"
    #         sender = settings.EMAIL_HOST_USER
    #         receivers = []
    #         for p in news.followers.all():
    #             if p.user != request.user:
    #                 receivers.append(p.user.email)
    #         if profile.status != 'gm':
    #             receivers.append('lukas.kozicki@gmail.com')
    #         send_mail(subject, message, sender, receivers)
    #
    #         messages.info(request, f'Twoja odpowiedź została zapisana!')
    #         return redirect('news:detail', news_id=news_id)
    # else:
    #     form = CreateNewsAnswerForm()

    context = {
        'page_title': announcement.title,
        'announcement': announcement,
        # 'form': form,
    }
    if profile in announcement.known_directly.all() or profile.status == 'gm':
        return render(request, 'communications/announcement.html', context)
    else:
        return redirect('home:dupa')
#
#
# @login_required
# def unfollow_news_view(request, news_id):
#     profile = request.user.profile
#     news = get_object_or_404(News, id=news_id)
#
#     if profile in news.allowed_profiles.all() or profile.status == 'gm':
#         news.followers.remove(profile)
#         messages.info(request, 'Przestałeś obserwować ogłoszenie!')
#         return redirect('news:detail', news_id=news_id)
#     else:
#         return redirect('home:dupa')
#
#
# @login_required
# def follow_news_view(request, news_id):
#     profile = request.user.profile
#     news = get_object_or_404(News, id=news_id)
#
#     if profile in news.allowed_profiles.all() or profile.status == 'gm':
#         news.followers.add(profile)
#         messages.info(request, 'Obserwujesz ogłoszenie!')
#         return redirect('news:detail', news_id=news_id)
#     else:
#         return redirect('home:dupa')
#
#
# #
# # @login_required
# # def survey_detail_view(request, survey_id):
# #     profile = request.user.profile
# #     survey = get_object_or_404(Survey, id=survey_id)
# #
# #     survey_seen_by = survey.seen_by.all()
# #     if profile not in survey_seen_by:
# #         survey.seen_by.add(profile)
# #
# #     options = survey.survey_options.all()\
# #         .prefetch_related('yes_voters', 'no_voters')\
# #         .select_related('author')
# #     answers = survey.survey_answers.all().select_related('author')
# #
# #     last_answer_seen_by_imgs = []
# #     if answers:
# #         last_answer = answers.order_by('-created_at')[0]
# #         if profile not in last_answer.seen_by.all():
# #             last_answer.seen_by.add(profile)
# #         last_answer_seen_by_imgs = (p.image for p in last_answer.seen_by.all())
# #
# #     if request.method == 'POST':
# #         answer_form = CreateSurveyAnswerForm(request.POST, request.FILES)
# #         option_form = CreateSurveyOptionForm(request.POST)
# #
# #         if answer_form.is_valid():
# #             answer = answer_form.save(commit=False)
# #             answer.survey = survey
# #             answer.author = request.user.profile
# #             answer_form.save()
# #
# #             subject = f"[RPG] Wypowiedż do ankiety: '{survey.title[:30]}...'"
# #             message = f"{profile} wypowiedział się co do ankiety '{survey.title}':\n" \
# #                       f"Ankieta: {request.get_host()}/news/survey-detail:{survey.id}/\n\n" \
# #                       f"Wypowiedź: {answer.text}"
# #             sender = settings.EMAIL_HOST_USER
# #             receivers = []
# #             for p in survey.addressees.all():
# #                 if p.user != request.user:
# #                     receivers.append(p.user.email)
# #             if profile.status != 'gm':
# #                 receivers.append('lukas.kozicki@gmail.com')
# #             send_mail(subject, message, sender, receivers)
# #
# #             messages.info(request, f'Twoja odpowiedź została zapisana!')
# #             return redirect('news:survey-detail', survey_id=survey_id)
# #
# #         elif option_form.is_valid():
# #             option = option_form.save(commit=False)
# #             option.survey = survey
# #             option.author = request.user.profile
# #             option_form.save()
# #
# #             messages.info(request, f'Powiadom uczestników o nowej opcji!')
# #             return redirect('news:survey-detail', survey_id=survey_id)
# #     else:
# #         answer_form = CreateSurveyAnswerForm()
# #         option_form = CreateSurveyOptionForm()
# #
# #     context = {
# #         'page_title': survey.title,
# #         'survey': survey,
# #         'options': options,
# #         'answers': answers,
# #         'survey_seen_by': survey_seen_by,
# #         'last_answer_seen_by_imgs': last_answer_seen_by_imgs,
# #         'answer_form': answer_form,
# #         'option_form': option_form
# #     }
# #     if profile in survey.addressees.all() or profile.status == 'gm':
# #         return render(request, 'news/survey_detail.html', context)
# #     else:
# #         return redirect('home:dupa')
#
#
#
# @login_required
# def vote_yes_view(request, survey_id, option_id):
#     profile = request.user.profile
#     option = get_object_or_404(SurveyOption, id=option_id)
#
#     if profile in option.survey.addressees.all() or profile.status == 'gm':
#         option.yes_voters.add(profile)
#         if profile in option.no_voters.all():
#             option.no_voters.remove(profile)
#
#         messages.info(request, 'Twój głos został dodany!')
#         return redirect('news:survey-detail', survey_id=survey_id)
#     else:
#         return redirect('home:dupa')
#
#
#
# @login_required
# def vote_no_view(request, survey_id, option_id):
#     profile = request.user.profile
#     option = get_object_or_404(SurveyOption, id=option_id)
#
#     if profile in option.survey.addressees.all() or profile.status == 'gm':
#         option.no_voters.add(profile)
#         if profile in option.yes_voters.all():
#             option.yes_voters.remove(profile)
#
#         messages.info(request, 'Twój głos został dodany!')
#         return redirect('news:survey-detail', survey_id=survey_id)
#     else:
#         return redirect('home:dupa')
#
#
#
# @login_required
# def unvote_view(request, survey_id, option_id):
#     profile = request.user.profile
#     option = get_object_or_404(SurveyOption, id=option_id)
#
#     if profile in option.survey.addressees.all() or profile.status == 'gm':
#         if profile in option.yes_voters.all():
#             option.yes_voters.remove(profile)
#         elif profile in option.no_voters.all():
#             option.no_voters.remove(profile)
#
#         messages.info(request, 'Twój głos został skasowany!')
#         return redirect('news:survey-detail', survey_id=survey_id)
#     else:
#         return redirect('home:dupa')
#
#
# #
# # @login_required
# # def survey_create_view(request):
# #     profile = request.user.profile
# #     if request.method == 'POST':
# #         form = CreateSurveyForm(authenticated_user=request.user, data=request.POST, files=request.FILES)
# #
# #         if form.is_valid():
# #             survey = form.save(commit=False)
# #             survey.author = request.user.profile
# #             survey.save()
# #             addressees = form.cleaned_data['addressees']
# #             addressees |= Profile.objects.filter(id=request.user.id)
# #             survey.addressees.set(addressees)
# #
# #             subject = f"[RPG] Nowa ankieta: '{survey.title[:30]}...'"
# #             message = f"{profile} przybił/a coś do słupa ogłoszeń.\n" \
# #                       f"Podejdź bliżej, aby się przyjrzeć: {request.get_host()}/news/survey-detail:{survey.id}/\n\n" \
# #                       f"Ogłoszenie: {survey.text}"
# #             sender = settings.EMAIL_HOST_USER
# #             receivers = []
# #             for p in survey.addressees.all():
# #                 if p.user != request.user:
# #                     receivers.append(p.user.email)
# #             if profile.status != 'gm':
# #                 receivers.append('lukas.kozicki@gmail.com')
# #             send_mail(subject, message, sender, receivers)
# #
# #             messages.info(request, f'Utworzono nową ankietę!')
# #             return redirect('news:survey-detail', survey_id=survey.id)
# #     else:
# #         form = CreateSurveyForm(authenticated_user=request.user)
# #
# #     context = {
# #         'page_title': 'Nowa ankieta',
# #         'form': form,
# #     }
# #     return render(request, 'news/survey_create.html', context)
#
#
#
# @login_required
# def survey_option_modify_view(request, survey_id, option_id):
#     option = get_object_or_404(SurveyOption, id=option_id)
#
#     if request.method == 'POST':
#         form = ModifySurveyOptionForm(request.POST, instance=option)
#
#         if form.is_valid():
#             form.save()
#             messages.info(request, f'Zmieniono opcję ankiety!')
#             return redirect('news:survey-detail', survey_id=survey_id)
#     else:
#         form = ModifySurveyOptionForm(instance=option)
#
#     context = {
#         'page_title': 'Zmiana opcji ankiety',
#         'form': form,
#     }
#     if request.user.profile == option.author:
#         return render(request, 'news/survey_option_modify.html', context)
#     else:
#         return redirect('home:dupa')
#
#
#
# @login_required
# def survey_option_delete_view(request, survey_id, option_id):
#     option = get_object_or_404(SurveyOption, id=option_id)
#     if request.user.profile == option.author:
#         option.delete()
#         return redirect('news:survey-detail', survey_id=survey_id)
#     else:
#         return redirect('home:dupa')
