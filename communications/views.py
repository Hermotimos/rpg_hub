from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db.models import Prefetch
from django.shortcuts import render, redirect

from communications.forms import (CreateTopicForm, AnnouncementCreateForm, DebateCreateForm, StatementCreateForm)
from communications.models import Topic, Thread, Debate, Announcement, Statement
from users.models import Profile


# TODO
#  1) main views separate? or separate templates based on 'thread_kind' param?
#  2) detail views - one for all, steer it with parameters; separate templates

#  TODO maybe make thread_map into file level constant; nested dicts:
#     thread_map = {
#         'Announcement': {
#           'form': AnnouncementCreateForm,
#           'verbose_name': "Ogłoszenie"},
#         'Debate': {
#           'form': DebateCreateForm,
#           'verbose_name': "Narada"},
#     }


@login_required
def announcements_view(request):
    profile = Profile.objects.get(id=request.session['profile_id'])
    
    if profile.status == 'gm':
        announcements = Announcement.objects.all()
    else:
        announcements = Announcement.objects.filter(known_directly=profile)

    announcements = announcements.prefetch_related(
        'statements__author', 'statements__seen_by').order_by('-created_at')
    
    topics = Topic.objects.filter(threads__in=announcements)
    topics = topics.prefetch_related(
        Prefetch('threads', queryset=announcements)).distinct()

    context = {
        'current_profile': profile,
        'page_title': 'Ogłoszenia',
        'topics': topics,
        'unseen_announcements': profile.unseen_announcements,
    }
    return render(request, 'communications/announcements.html', context)


@login_required
def announcement_view(request, thread_id):
    profile = Profile.objects.get(id=request.session['profile_id'])
    
    announcements = Announcement.objects.prefetch_related(
        'statements__seen_by', 'statements__author', 'followers',
        'known_directly')
    announcement = announcements.get(id=thread_id)

    # Update all statements to be seen by the profile
    SeenBy = Statement.seen_by.through
    relations = []
    for statement in announcement.statements.all():
        relations.append(
            SeenBy(statement_id=statement.id, profile_id=profile.id))
        # print(relations)
    SeenBy.objects.bulk_create(relations, ignore_conflicts=True)

    statement_form = StatementCreateForm(
        data=request.POST or None,
        files=request.FILES or None,
        profile=profile,
        thread_kind='Announcement',
        known_directly=[],
        initial={'author': profile})
    
    if statement_form.is_valid():
        statement = statement_form.save(commit=False)
        statement.thread = announcement
        statement.save()

        subject = f"[RPG] Odpowiedź na Ogłoszenie: '{announcement.title[:30]}...'"
        message = f"{profile}:\n{request.get_host()}{announcement.get_absolute_url()}/\n\n"
        sender = settings.EMAIL_HOST_USER
        receivers = []
        for profile in announcement.followers.all():
            if profile.user != request.user:
                receivers.append(profile.user.email)
        if profile.status != 'gm':
            receivers.append('lukas.kozicki@gmail.com')
        send_mail(subject, message, sender, receivers)

        messages.info(request, f'Dodano wypowiedź!')
        return redirect(
            f'communications:announcement', thread_id=announcement.id)

    context = {
        'current_profile': profile,
        'page_title': announcement.title,
        'announcement': announcement,
        'form': statement_form,
    }
    if profile in announcement.known_directly.all() or profile.status == 'gm':
        return render(request, 'communications/announcement.html', context)
    else:
        return redirect('home:dupa')
    

@login_required
def create_topic_view(request, thread_kind: str):
    profile = Profile.objects.get(id=request.session['profile_id'])
    
    form = CreateTopicForm(request.POST or None)
    if form.is_valid():
        topic = form.save()
        messages.info(
            request, f"Utworzono nowy temat: '{topic.title}'!")
        return redirect('communications:create-thread', thread_kind=thread_kind)

    context = {
        'current_profile': profile,
        'page_title': "Nowy temat",
        'form_1': form,
    }
    return render(request, '_create_form.html', context)


@login_required
def create_thread_view(request, thread_kind):
    profile = Profile.objects.get(id=request.session['profile_id'])

    thread_map = {
        'Announcement': [AnnouncementCreateForm, "Ogłoszenie"],
        'Debate': [DebateCreateForm, "Narada"],
    }

    thread_form = thread_map[thread_kind][0](
        data=request.POST or None,
        files=request.FILES or None,
        profile=profile)
    
    statement_form = StatementCreateForm(
        data=request.POST or None,
        files=request.FILES or None,
        profile=profile,
        thread_kind=thread_kind,
        known_directly=[],
        initial={'author': profile.id})

    if thread_form.is_valid() and statement_form.is_valid():
        thread = thread_form.save(commit=False)
        thread.kind = thread_kind
        thread.save()
        
        known_directly = thread_form.cleaned_data['known_directly']
        known_directly |= Profile.objects.filter(id=request.user.id)
        thread.known_directly.set(known_directly)
        thread.followers.set(known_directly)

        statement = statement_form.save(commit=False)
        statement.thread = thread
        statement.author = profile
        statement.save()

        # TODO USE send_emails - REWORK send_emails so that it is provied with data?
        # if profile == demand.author:
        #     informed_ids = [demand.addressee.id]
        # else:
        #     informed_ids = [demand.author.id]
        # send_emails(request, informed_ids, demand_answer=answer)
        
        subject = f"[RPG] Nowość: {thread_map[thread_kind][1]} '{thread.title[:30]}...'"
        message = f"{profile}:\n{request.get_host()}{thread.get_absolute_url()}/\n\n"
        sender = settings.EMAIL_HOST_USER
        receivers = []
        for profile in thread.followers.all():
            if profile.user != request.user:
                receivers.append(profile.user.email)
        if profile.status != 'gm':
            receivers.append("lukas.kozicki@gmail.com")
        send_mail(subject, message, sender, receivers)

        messages.info(request, f"Utworzono {thread_map[thread_kind][1]}!")
        return redirect(
            f'communications:{thread_kind.lower()}', thread_id=thread.id)

    context = {
        'current_profile': profile,
        'page_title': f"Nowe {thread_map[thread_kind][1]}",
        'form_1': thread_form,
        'form_2': statement_form,
    }
    return render(request, '_create_form.html', context)


#
#
# @login_required
# def unfollow_news_view(request, news_id):
#     profile = Profile.objects.get(id=request.session['profile_id'])
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
#     profile = Profile.objects.get(id=request.session['profile_id'])
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
#
#
# @login_required
# def vote_yes_view(request, survey_id, option_id):
#     profile = Profile.objects.get(id=request.session['profile_id'])
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
#     profile = Profile.objects.get(id=request.session['profile_id'])
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
#     profile = Profile.objects.get(id=request.session['profile_id'])
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
# #     profile = Profile.objects.get(id=request.session['profile_id'])
# #     if request.method == 'POST':
# #         form = CreateSurveyForm(profile=profile, data=request.POST, files=request.FILES)
# #
# #         if form.is_valid():
# #             survey = form.save(commit=False)
# #             survey.author = profile
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
# #         form = CreateSurveyForm(profile=profile)
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
#     profile = Profile.objects.get(id=request.session['profile_id'])
#
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
#     if profile == option.author:
#         return render(request, 'news/survey_option_modify.html', context)
#     else:
#         return redirect('home:dupa')
#
#
#
# @login_required
# def survey_option_delete_view(request, survey_id, option_id):
#     profile = Profile.objects.get(id=request.session['profile_id'])
#
#     option = get_object_or_404(SurveyOption, id=option_id)
#     if profile == option.author:
#         option.delete()
#         return redirect('news:survey-detail', survey_id=survey_id)
#     else:
#         return redirect('home:dupa')
