from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db.models import Prefetch, Q
from django.shortcuts import render, redirect, get_object_or_404

from communications.forms import (
    AnnouncementCreateForm,
    DebateCreateForm,
    StatementCreateForm,
    ThreadEditTagsForm,
    ThreadTagEditFormSet,
    ThreadTagEditFormSetHelper,
    TopicCreateForm,
)
from communications.models import (
    Announcement,
    Statement,
    Thread,
    ThreadTag,
    Topic,
)
from users.models import Profile

# TODO
#  1) main views separate? or separate templates based on 'thread_kind' param?
#  2) detail views - one for all, steer it with parameters; separate templates


THREAD_MAP = {
    'Announcement': {
      'name': "Ogłoszenie",
      'text': "Nowe Ogłoszenie",
      'form': AnnouncementCreateForm,
    },
    'Debate': {
      'name': "Narada",
      'text': "Nowa Narada",
      'form': DebateCreateForm,
    },
}


def thread_inform(request, thread, tag_title):
    informed_ids = [
        k for k, v_list in request.POST.items() if 'on' in v_list]
    thread.known_directly.add(*informed_ids)
    thread.followers.add(*informed_ids)
    send_mail(
        subject=f"[RPG] Udostępnienie Ogłoszenia: '{thread.title}'",
        message=f"{request.get_host()}{thread.get_absolute_url()}/",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[
            p.user.email for p in Profile.objects.filter(
                id__in=informed_ids)])
    messages.info(request, f'Poinformowano wybranych Graczy!')
    return redirect(
        'communications:thread', thread_id=thread.id, tag_title=tag_title)


@login_required
def announcements_view(request, tag_title):
    current_profile = Profile.objects.get(id=request.session['profile_id'])
    
    announcements = Announcement.objects.prefetch_related(
        'statements__author', 'statements__seen_by', 'tags__author', 'topic',
        'followers')
    announcements = announcements.order_by('-created_at')
    if current_profile.status != 'gm':
        announcements = announcements.filter(known_directly=current_profile)
    if tag_title != 'None':
        announcements = announcements.filter(tags__title=tag_title)
        
    unseen_announcements = announcements.filter(
        id__in=current_profile.unseen_announcements)

    topics = Topic.objects.filter(threads__in=announcements)
    topics = topics.prefetch_related(
        Prefetch('threads', queryset=announcements)).distinct()
    
    tags = ThreadTag.objects.filter(author=current_profile, kind='Announcement')
    formset = ThreadTagEditFormSet(
        data=request.POST or None,
        queryset=tags)
    
    for form in formset:
        form.initial['kind'] = 'Announcement'
        form.initial['author'] = current_profile
        
    if request.method == 'GET':
        if tag_id := request.GET.get('tag', []):
            tag = ThreadTag.objects.get(id=tag_id)
            return redirect('communications:announcements', tag_title=tag.title)

    elif request.method == 'POST':
        if not formset.is_valid():
            if "Thread tag z tymi Title i Author" in str(formset.errors):
                messages.warning(request, "Zduplikowany tag!")
            messages.warning(request, "Popraw wskazane pola!")
        else:
            changed = False
            for form in formset:
                if not form.is_valid():
                    messages.warning(request, form.errors)
                else:
                    # Ignore empty extra forms
                    if not form.cleaned_data:
                        continue
                        
                    # Deletion
                    elif form.cleaned_data.get('DELETE'):
                        tag = form.cleaned_data.get('id')
                        if tag:
                            tag.delete()
                            changed = True
                            messages.success(request, f"Usunięto tag '{tag}'!")
                        else:
                            messages.warning(
                                request, "Nowy tag zaznaczony do usunięcia!")

                    # Creation / Modification
                    else:
                        tag = form.save(commit=False)
                        tag.author = form.cleaned_data['author']
                        tag.save()
                        if form.has_changed():
                            changed = True
                            messages.success(request, f"Zmieniono: {tag}!")
            if changed:
                return redirect(
                    'communications:announcements', tag_title=tag_title)
            else:
                messages.warning(request, "Nie dokonano żadnych zmian!")
                return redirect(
                    'communications:announcements', tag_title=tag_title)

    context = {
        'current_profile': current_profile,
        'page_title': 'Ogłoszenia',
        'topics': topics,
        'unseen_announcements': unseen_announcements,
        'tag_title': tag_title,
        'tags': tags,
        'formset': formset,
        'formset_helper': ThreadTagEditFormSetHelper(),
    }
    return render(request, 'communications/announcements.html', context)


@login_required
def thread_view(request, thread_id, tag_title):
    current_profile = Profile.objects.get(id=request.session['profile_id'])

    threads = Thread.objects.prefetch_related(
        'statements__seen_by', 'statements__author', 'followers',
        'known_directly')
    thread = threads.get(id=thread_id)
    known_directly = thread.known_directly.all()

    # Update all statements to be seen by the profile
    SeenBy = Statement.seen_by.through
    relations = []
    for statement in thread.statements.all():
        relations.append(
            SeenBy(statement_id=statement.id, profile_id=current_profile.id))
    SeenBy.objects.bulk_create(relations, ignore_conflicts=True)

    # Create ThreadEditTagsForm and StatementCreateForm
    # Check if custom inform form activated, if not then StatementCreateForm,
    # if not then ThreadEditTagsForm: this order ensures correct handling, as
    # each form redirects if valid (and ThreadEditTagsForm is always invalid).
    thread_tags_form = ThreadEditTagsForm(
        data=request.POST or None,
        current_profile=current_profile,
        thread_kind=thread.kind,
        instance=thread)
    statement_form = StatementCreateForm(
        data=request.POST or None,
        files=request.FILES or None,
        current_profile=current_profile,
        thread_kind=thread.kind,
        known_directly=[],
        initial={'author': current_profile})

    if request.method == 'POST' and 'Announcement' in request.POST:
        thread_inform(request, thread, tag_title)
        return redirect(
            'communications:thread', thread_id=thread.id, tag_title=tag_title)

    if statement_form.is_valid():
        statement = statement_form.save(commit=False)
        statement.thread = thread
        statement.save()
        send_mail(
            subject=f"[RPG] Nowa wypowiedź: '{thread.title}'",
            message=f"{request.get_host()}{thread.get_absolute_url()}/",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[
                p.user.email for p in known_directly if p != current_profile]
        )
        messages.info(request, f"Dodano wypowiedź!")
        return redirect(
            'communications:thread', thread_id=thread.id, tag_title=tag_title)
    
    if thread_tags_form.is_valid():
        thread_tags_form.save()
        messages.info(request, f"Zapisano zmiany!")
        return redirect(
            'communications:thread', thread_id=thread.id, tag_title=tag_title)

    context = {
        'current_profile': current_profile,
        'page_title': thread.title,
        'thread': thread,
        'tag_title': tag_title,
        'form_1': statement_form,
        'thread_tags_form': thread_tags_form,
    }
    if current_profile in known_directly or current_profile.status == 'gm':
        return render(request, 'communications/thread.html', context)
    else:
        return redirect('home:dupa')
    

@login_required
def create_topic_view(request, thread_kind: str):
    current_profile = Profile.objects.get(id=request.session['profile_id'])
    
    form = TopicCreateForm(request.POST or None)
    if form.is_valid():
        topic = form.save()
        messages.info(
            request, f"Utworzono nowy temat: '{topic.title}'!")
        return redirect('communications:create-thread', thread_kind=thread_kind)

    context = {
        'current_profile': current_profile,
        'page_title': "Nowy temat",
        'form_1': form,
    }
    return render(request, 'create_form.html', context)


@login_required
def create_thread_view(request, thread_kind):
    current_profile = Profile.objects.get(id=request.session['profile_id'])

    thread_form = THREAD_MAP[thread_kind]['form'](
        data=request.POST or None,
        files=request.FILES or None,
        current_profile=current_profile)
    
    statement_form = StatementCreateForm(
        data=request.POST or None,
        files=request.FILES or None,
        current_profile=current_profile,
        thread_kind=thread_kind,
        known_directly=[],
        initial={'author': current_profile.id})

    if thread_form.is_valid() and statement_form.is_valid():
        thread = thread_form.save(commit=False)
        thread.kind = thread_kind
        thread.save()
        
        known_directly = thread_form.cleaned_data['known_directly']
        known_directly |= Profile.objects.filter(
            Q(id=current_profile.id) | Q(status='gm'))
        print(known_directly)
        thread.known_directly.set(known_directly)
        thread.followers.set(known_directly)

        statement = statement_form.save(commit=False)
        statement.thread = thread
        statement.author = current_profile
        statement.save()

        send_mail(
            subject=f"[RPG] {THREAD_MAP[thread_kind]['text']}: '{thread}'",
            message=f"{request.get_host()}{thread.get_absolute_url()}/",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[
                p.user.email for p in known_directly if p != current_profile])

        messages.info(request, f"Utworzono {THREAD_MAP[thread_kind]['name']}!")
        return redirect(
            'communications:thread', thread_id=thread.id, tag_title=None)

    context = {
        'current_profile': current_profile,
        'page_title': f"{THREAD_MAP[thread_kind]['text']}",
        'form_1': thread_form,
        'form_2': statement_form,
    }
    return render(request, 'create_form.html', context)


@login_required
def unfollow_thread_view(request, thread_id):
    current_profile = Profile.objects.get(id=request.session['profile_id'])
    
    thread = get_object_or_404(Thread, id=thread_id)
    if current_profile in thread.known_directly.all():
        thread.followers.remove(current_profile)
        messages.info(request, f"Przestałeś obserwować \"{thread}\"!")
        return redirect(request.META.get('HTTP_REFERER', '/'))
    else:
        return redirect('home:dupa')


@login_required
def follow_thread_view(request, thread_id):
    current_profile = Profile.objects.get(id=request.session['profile_id'])
    
    thread = get_object_or_404(Thread, id=thread_id)
    if current_profile in thread.known_directly.all():
        thread.followers.add(current_profile)
        messages.info(request, f"Zacząłeś obserwować \"{thread}\"!")
        return redirect(request.META.get('HTTP_REFERER', '/'))
    else:
        return redirect('home:dupa')



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
