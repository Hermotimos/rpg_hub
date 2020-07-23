from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.shortcuts import render, redirect, get_object_or_404

from debates.forms import CreateRemarkForm, CreateDebateForm, CreateTopicForm
from debates.models import Topic, Debate
from rpg_project.utils import send_emails, handle_inform_form
from users.models import Profile


@login_required
def debates_main_view(request):
    profile = request.user.profile
    debates = Debate.objects.all().prefetch_related('known_directly')
    if profile.status != 'gm':
        debates = Debate.objects.filter(known_directly=profile)
        debates = debates.select_related('chronicle_event__game')
        debates = debates.prefetch_related('known_directly')

    topics = Topic.objects.filter(debates__in=debates)
    topics = topics.prefetch_related(Prefetch('debates', queryset=debates))
    topics = topics.distinct()

    context = {
        'page_title': 'Narady',
        'topics': topics,
    }
    return render(request, 'debates/main.html', context)


@login_required
def create_topic_view(request):
    profile = request.user.profile
    if request.method == 'POST':
        topic_form = CreateTopicForm(request.POST)
        debate_form = CreateDebateForm(authenticated_user=request.user,
                                       data=request.POST)
        remark_form = CreateRemarkForm(request.POST, request.FILES,
                                       debate_id=0)

        if topic_form.is_valid() and debate_form.is_valid() \
                and remark_form.is_valid():
            topic = topic_form.save()

            debate = debate_form.save(commit=False)
            debate.topic = topic
            debate.save()

            new_known_directly = debate_form.cleaned_data['known_directly']
            new_known_directly |= Profile.objects.filter(id=profile.id)
            debate.known_directly.add(*list(new_known_directly))

            remark = remark_form.save(commit=False)
            remark.debate = debate
            remark.save()
            
            informed_ids = [p.id for p in new_known_directly if p != profile]

            send_emails(request, informed_ids, debate_new_topic=debate)
            messages.info(request, f'Utworzono nową naradę w nowym temacie!')
            return redirect('debates:debate', debate_id=debate.id)
    else:
        topic_form = CreateTopicForm()
        debate_form = CreateDebateForm(authenticated_user=request.user)
        remark_form = CreateRemarkForm(initial={'author': request.user},
                                       debate_id=0)

    context = {
        'page_title': 'Nowa narada w nowym temacie',
        'topic_form': topic_form,
        'debate_form': debate_form,
        'remark_form': remark_form,
    }
    return render(request, 'debates/create_topic.html', context)


@login_required
def create_debate_view(request, topic_id):
    profile = request.user.profile
    topic = get_object_or_404(Topic, id=topic_id)

    if request.method == 'POST':
        debate_form = CreateDebateForm(authenticated_user=request.user,
                                       data=request.POST)
        remark_form = CreateRemarkForm(request.POST, request.FILES,
                                       debate_id=0)
        
        if debate_form.is_valid() and remark_form.is_valid():
            debate = debate_form.save(commit=False)
            debate.topic = Topic.objects.get(id=topic_id)
            debate.save()
            
            new_known_directly = debate_form.cleaned_data['known_directly']
            new_known_directly |= Profile.objects.filter(id=profile.id)
            debate.known_directly.add(*list(new_known_directly))

            remark = remark_form.save(commit=False)
            remark.debate = debate
            remark.save()
            
            informed_ids = [p.id for p in new_known_directly if p != profile]

            send_emails(request, informed_ids, debate_new=debate)
            messages.info(request, f'Utworzono nową naradę!')
            return redirect('debates:debate', debate_id=debate.id)
    else:
        debate_form = CreateDebateForm(authenticated_user=request.user)
        remark_form = CreateRemarkForm(initial={'author': request.user},
                                       debate_id=0)

    context = {
        'page_title': 'Nowa narada',
        'debate_form': debate_form,
        'remark_form': remark_form,
        'topic': topic
    }
    return render(request, 'debates/create_debate.html', context)


@login_required
def debate_view(request, debate_id):
    profile = request.user.profile
    debate = Debate.objects.select_related().get(id=debate_id)
    topic = debate.topic

    debate_known_directly = debate.known_directly.exclude(status='gm')
    remarks = debate.remarks.all().select_related('author__profile')

    last_remark = None
    last_remark_seen_by_imgs = []
    if debate.remarks.exclude(author__profile__status='gm'):
        last_remark = debate.remarks.order_by('-created_at')[0]
        if not debate.is_ended:
            seen_by = last_remark.seen_by.all()
            if profile not in seen_by:
                last_remark.seen_by.add(profile)
            last_remark_seen_by_imgs = [
                p.image for p in last_remark.seen_by.all()
            ]

    if request.method == 'POST':
        handle_inform_form(request)

    # REMARK FORM
    if request.method == 'POST' and 'debate' not in request.POST:
        form = CreateRemarkForm(request.POST, request.FILES,
                                debate_id=debate_id)
        if form.is_valid():
            remark = form.save(commit=False)
            remark.debate = debate
            remark.save()

            informed_ids = [p.id for p in debate_known_directly if p != profile]

            send_emails(request, informed_ids, debate_remark=debate)
            if informed_ids:
                messages.info(request, f'Twój głos zabrzmiał w naradzie!')
            return redirect('debates:debate', debate_id=debate_id)
    else:
        form = CreateRemarkForm(initial={'author': request.user},
                                debate_id=debate_id)

    context = {
        'page_title': debate.name,
        'topic': topic,
        'debate': debate,
        'debate_known_directly': debate_known_directly,
        'remarks': remarks,
        'last_remark': last_remark,
        'last_remark_seen_by_imgs': last_remark_seen_by_imgs,
        'form': form,
    }
    return render(request, 'debates/debate.html', context)


# @login_required
# def unfollow_debate_view(request, debate_id):
#     profile = request.user.profile
#     debate = get_object_or_404(Debate, id=debate_id)
#     if profile in debate.known_directly.all() or profile.status == 'gm':
#         debate.followers.remove(profile)
#         messages.info(request, 'Przestałeś uważnie uczestniczyć w naradzie!')
#         return redirect('debates:debate', debate_id=debate_id)
#     else:
#         return redirect('home:dupa')
#
#
# @login_required
# def follow_debate_view(request, debate_id):
#     profile = request.user.profile
#     debate = get_object_or_404(Debate, id=debate_id)
#     if profile in debate.known_directly.all() or profile.status == 'gm':
#         debate.followers.add(profile)
#         messages.info(request, 'Od teraz uważnie uczestniczysz w naradzie!')
#         return redirect('debates:debate', debate_id=debate_id)
#     else:
#         return redirect('home:dupa')
