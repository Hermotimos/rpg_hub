from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db.models import Prefetch, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie

from communications.forms import (
    AnnouncementCreateForm,
    DebateCreateForm,
    StatementCreateForm,
    ThreadEditTagsForm,
    ThreadTagEditFormSet,
    ThreadTagEditFormSetHelper,
)
from communications.models import (
    Statement,
    Thread,
    ThreadTag,
)
from rpg_project.utils import auth_profile, OrderByPolish
from users.models import Profile


# TODO
#  1) main views separate? or separate templates based on 'thread_kind' param?
#  2) detail views - one for all, steer it with parameters; separate templates


THREADS_MAP = {
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
PROFILE_THREADS = ["Debate", "Plan"]
USER_THREADS = ["Announcement", "Demand"]


def get_initiator(thread: Thread):
    """Get URL of the Profile who "initiated" the Thread.
    Take the author of first Statement as the initiator; only in Announcements
    take the first player's or NPC's Profile as initiator.
    """
    if not thread.statements.exists():
        return None
    if thread.kind == "Debate":
        for statement in thread.statements.all():
            if statement.author.status != 'gm':
                return statement.author
    return thread.statements.first().author


def thread_inform(current_profile, request, thread, tag_title):
    informed_ids = [k for k, v_list in request.POST.items() if 'on' in v_list]
    informed = Profile.objects.filter(id__in=informed_ids)
    thread.participants.add(*informed)
    thread.followers.add(*informed)
    
    recipients = Profile.objects.filter(id__in=informed_ids)
    if current_profile.user.profiles.filter(status="gm").exists():
        # Exclude via user, because all NPCs are linked with GM via user
        recipients = recipients.exclude(user__profiles__status='gm')

    send_mail(
        subject=f"[RPG] Udostępnienie Ogłoszenia: '{thread.title}'",
        message=f"{request.get_host()}{thread.get_absolute_url()}",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[p.user.email for p in recipients])
    messages.info(request, f'Poinformowano wybranych Graczy!')
    return redirect('communications:thread', thread_id=thread.id, tag_title=tag_title)


def get_threads(current_profile, thread_kind):
    """Get threads with prefetched related objects. Filter threads depending
    whether it's a per-profile or per-user ThreadKind.
    """
    threads = Thread.objects.filter(kind=thread_kind)
    
    if current_profile.can_view_all:
        threads = threads
    elif thread_kind in PROFILE_THREADS:
        threads = threads.filter(participants=current_profile)
    elif thread_kind in USER_THREADS:
        threads = threads.filter(participants__in=current_profile.user.profiles.all())
    else:
        raise ValueError("Podany thread_kind nie występuje!")
    
    threads = threads.prefetch_related(
        'statements__author__character',
        'tags__author',
        'events__game',
        'participants__character',
        'followers',
    )
    return threads


@login_required
@auth_profile(['all'])
def threads_view(request, thread_kind, tag_title):
    current_profile = request.current_profile

    threads = get_threads(current_profile, thread_kind)
    if tag_title != 'None':
        threads = threads.filter(tags__title=tag_title)

    if thread_kind == 'Announcement':
        page_title = "Ogłoszenia"
        unseen = threads.filter(id__in=current_profile.unseen_announcements)
    elif thread_kind == 'Debate':
        page_title = "Narady"
        unseen = threads.filter(id__in=current_profile.unseen_debates)
    else:
        page_title = "TODO"
        unseen = Thread.objects.none()
    threads = threads.exclude(id__in=unseen).order_by(OrderByPolish('title'))

    # Annotate threads with attribute 'initiator'
    for thread in threads:
        thread.initiator = get_initiator(thread)
    for thread_unseen in unseen:
        thread_unseen.initiator = get_initiator(thread_unseen)

    tags = ThreadTag.objects.filter(author=current_profile, kind=thread_kind)
    formset = ThreadTagEditFormSet(
        data=request.POST or None,
        queryset=tags)
    
    for form in formset:
        form.initial['kind'] = thread_kind
        form.initial['author'] = current_profile
        
    if request.method == 'GET':
        if tag_id := request.GET.get('tag', []):
            tag = ThreadTag.objects.get(id=tag_id)
            return redirect('communications:threads', thread_kind=thread_kind, tag_title=tag.title)

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
                            messages.warning(request, "Nowy tag zaznaczony do usunięcia!")

                    # Creation / Modification
                    else:
                        tag = form.save(commit=False)
                        tag.author = form.cleaned_data['author']
                        tag.save()
                        if form.has_changed():
                            changed = True
                            messages.success(request, f"Zmieniono: {tag}!")
            if changed:
                return redirect('communications:threads', thread_kind=thread_kind, tag_title=tag_title)
            else:
                messages.warning(request, "Nie dokonano żadnych zmian!")
                return redirect('communications:threads', thread_kind=thread_kind, tag_title=tag_title)

    context = {
        'page_title': page_title,
        'threads': threads,
        'unseen': unseen,
        'thread_kind': thread_kind,
        'tag_title': tag_title,
        'tags': tags,
        'formset': formset,
        'formset_helper': ThreadTagEditFormSetHelper(),
    }
    return render(request, 'communications/threads.html', context)


@login_required
@auth_profile(['all'])
def thread_view(request, thread_id, tag_title):
    current_profile = request.current_profile

    tags = ThreadTag.objects.filter(
        author=current_profile, kind=Thread.objects.get(id=thread_id).kind).select_related('author')
    threads = Thread.objects.prefetch_related(
        Prefetch('tags', queryset=tags),
        'statements__seen_by',
        'statements__author__user',
        'statements__author__character',
        'followers',
        'participants')
    thread = threads.get(id=thread_id)
    
    informables = thread.informables()
    if current_profile.status != 'gm':
        informables = informables.filter(
            character__in=current_profile.character.acquaintaned_to.all())

    # Update all statements to be seen by the profile
    SeenBy = Statement.seen_by.through
    relations = []
    for statement in thread.statements.all():
        relations.append(SeenBy(statement_id=statement.id, profile_id=current_profile.id))
    SeenBy.objects.bulk_create(relations, ignore_conflicts=True)

    # Create ThreadEditTagsForm and StatementCreateForm
    # Check if custom inform form activated, if not then StatementCreateForm,
    # if not then ThreadEditTagsForm: this order ensures correct handling, as
    # each form redirects if valid (and ThreadEditTagsForm is always invalid).
    thread_tags_form = ThreadEditTagsForm(
        data=request.POST or None,
        instance=thread,
        tags=tags)
    statement_form = StatementCreateForm(
        data=request.POST or None,
        files=request.FILES or None,
        current_profile=current_profile,
        thread_kind=thread.kind,
        participants=thread.participants.all(),
        initial={'author': current_profile})

    if request.method == 'POST' and any(
        [thread_kind in request.POST.keys() for thread_kind in THREADS_MAP.keys()]
    ):
        # Enters only when request.POST has 'Debate', 'Announcement' etc. key
        # <QueryDict: {'csrfmiddlewaretoken': [...], '145': ['on'], 'Debate': ['56']}>
        thread_inform(current_profile, request, thread, tag_title)
        return redirect('communications:thread', thread_id=thread.id, tag_title=tag_title)

    if statement_form.is_valid():
        statement = statement_form.save(commit=False, thread_kind=thread.kind)
        statement.thread = thread
        statement.save()
        try:
            statement.seen_by.add(current_profile)
        except ValueError as exc:
            # Ignore ValueErrors caused by Statement deleted by signal
            # This happens in cases of doubled Statement's
            if 'needs to have a value for field "id"' not in exc.args[0]:
                raise exc
            
        send_mail(
            subject=f"[RPG] Nowa wypowiedź: '{thread.title}'",
            message=f"{request.get_host()}{thread.get_absolute_url()}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[
                p.user.email for p in thread.followers.exclude(id=current_profile.id)])
        messages.info(request, "Dodano wypowiedź!")
        return redirect('communications:thread', thread_id=thread.id, tag_title=tag_title)
    
    if thread_tags_form.is_valid():
        thread_tags_form.save()
        messages.info(request, "Zapisano zmiany!")
        return redirect('communications:thread', thread_id=thread.id, tag_title=tag_title)

    context = {
        'page_title': thread.title,
        'thread': thread,
        'tag_title': tag_title,
        'informables': informables,
        'form_1': statement_form,
        'thread_tags_form': thread_tags_form,
    }
    if current_profile in thread.participants.all() or current_profile.status == 'gm':
        return render(request, 'communications/thread.html', context)
    else:
        return redirect('users:dupa')
    

@cache_page(60 * 60 * 24)
@vary_on_cookie
@login_required
@auth_profile(['all'])
def create_thread_view(request, thread_kind):
    current_profile = request.current_profile

    thread_form = THREADS_MAP[thread_kind]['form'](
        data=request.POST or None,
        files=request.FILES or None,
        current_profile=current_profile)
    
    statement_form = StatementCreateForm(
        data=request.POST or None,
        files=request.FILES or None,
        current_profile=current_profile,
        thread_kind=thread_kind,
        participants=[],
        initial={'author': current_profile.id})

    if thread_form.is_valid() and statement_form.is_valid():
        thread = thread_form.save(commit=False)
        thread.kind = thread_kind
        thread.save()
        
        participants = thread_form.cleaned_data['participants']
        if thread_kind in USER_THREADS:
            # USER_THREADS show users as participants - translate to Profiles
            participants = Profile.objects.filter(user__in=participants)
        participants |= Profile.objects.filter(
            Q(id=current_profile.id) | Q(status='gm'))
        thread.participants.set(participants)
        thread.followers.set(participants)

        statement = statement_form.save(commit=False)
        statement.thread = thread
        statement.save()
        statement.seen_by.add(current_profile)

        send_mail(
            subject=f"[RPG] {THREADS_MAP[thread_kind]['text']}: '{thread}'",
            message=f"{request.get_host()}{thread.get_absolute_url()}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[
                p.user.email for p in thread.followers.exclude(
                    id__in=current_profile.user.profiles.all())
            ]
        )
        messages.info(request, f"{THREADS_MAP[thread_kind]['text']}: '{thread}!")
        return redirect('communications:thread', thread_id=thread.id, tag_title=None)

    context = {
        'page_title': f"{THREADS_MAP[thread_kind]['text']}",
        'form_1': thread_form,
        'form_2': statement_form,
    }
    return render(request, 'create_form.html', context)


@login_required
@auth_profile(['all'])
def unfollow_thread_view(request, thread_id):
    current_profile = request.current_profile
    
    thread = get_object_or_404(Thread, id=thread_id)
    if current_profile in thread.participants.all() or current_profile.can_view_all:
        thread.followers.remove(current_profile)
        messages.info(request, f"Przestałeś obserwować \"{thread}\"!")
        return redirect(request.META.get('HTTP_REFERER', '/'))
    else:
        return redirect('users:dupa')


@login_required
@auth_profile(['all'])
def follow_thread_view(request, thread_id):
    current_profile = request.current_profile
    
    thread = get_object_or_404(Thread, id=thread_id)
    if current_profile in thread.participants.all() or current_profile.can_view_all:
        thread.followers.add(current_profile)
        messages.info(request, f"Zacząłeś obserwować \"{thread}\"!")
        return redirect(request.META.get('HTTP_REFERER', '/'))
    else:
        return redirect('users:dupa')



#
# @login_required
# def vote_yes_view(request, survey_id, option_id):
#     profile = request.current_profile
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
#         return redirect('users:dupa')
#
#
#
# @login_required
# def vote_no_view(request, survey_id, option_id):
#     profile = request.current_profile
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
#         return redirect('users:dupa')
#
#
#
# @login_required
# def unvote_view(request, survey_id, option_id):
#     profile = request.current_profile
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
#         return redirect('users:dupa')
#
#
# #
# # @login_required
# # def survey_create_view(request):
# #     profile = request.current_profile
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
#     profile = request.current_profile
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
#         return redirect('users:dupa')
#
#
#
# @login_required
# def survey_option_delete_view(request, survey_id, option_id):
#     profile = request.current_profile
#
#     option = get_object_or_404(SurveyOption, id=option_id)
#     if profile == option.author:
#         option.delete()
#         return redirect('news:survey-detail', survey_id=survey_id)
#     else:
#         return redirect('users:dupa')



from communications.models import Room, Message
from django.http import HttpResponse, JsonResponse

# Create your views here.
def home(request):
    return render(request, 'communications/home.html')

def room(request, room):
    username = request.GET.get('username')
    room_details = Room.objects.get(name=room)
    return render(request, 'communications/room.html', {
        'username': username,
        'room': room,
        'room_details': room_details
    })

def checkview(request):
    room = request.POST['room_name']
    username = request.POST['username']

    if Room.objects.filter(name=room).exists():
        return redirect('/communications/'+room+'/?username='+username)
    else:
        new_room = Room.objects.create(name=room)
        new_room.save()
        return redirect('/communications/'+room+'/?username='+username)

def send(request):
    message = request.POST['message']
    username = request.POST['username']
    room_id = request.POST['room_id']

    new_message = Message.objects.create(value=message, user=username, room=room_id)
    new_message.save()
    return HttpResponse('Message sent successfully')

def getMessages(request, room):
    room_details = Room.objects.get(name=room)

    messages = Message.objects.filter(room=room_details.id)
    print(room, messages)
    return JsonResponse({"messages": list(messages.values())})

