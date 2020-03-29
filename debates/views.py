from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import (Count, Case, When, IntegerField, Max, Min,
                              Prefetch, Q)
from django.shortcuts import render, redirect, get_object_or_404

from debates.forms import CreateRemarkForm, CreateDebateForm, CreateTopicForm
from debates.models import Topic, Debate
from rpg_project.utils import query_debugger, send_emails


@query_debugger
@login_required
def debates_main_view(request):
    profile = request.user.profile
    if profile.status == 'gm':
        topics = Topic.objects.all()
        debates = Debate.objects.all().prefetch_related('allowed_profiles')
    else:
        topics = Topic.objects.filter(allowed_profiles=profile)
        debates = Debate.objects.filter(allowed_profiles=profile).prefetch_related('allowed_profiles')

    topics = topics.prefetch_related(
        Prefetch(
            'debates',
            queryset=debates.annotate(
                first_player_remark_date=Min('remarks__date_posted'),
                last_player_remark_date=Max('remarks__date_posted'),
                player_remarks_count=Count(
                    Case(
                        When(
                            ~Q(remarks__author__profile__status='gm'), then=1
                        ),
                        output_field=IntegerField()
                    )
                )
            )
        ),
    )

    context = {
        'page_title': 'Narady',
        'topics': topics,
    }
    return render(request, 'debates/main.html', context)


@query_debugger
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

            new_allowed_profiles = debate_form.cleaned_data['allowed_profiles']
            debate.allowed_profiles.add(*list(new_allowed_profiles))
            debate.followers.add(*list(new_allowed_profiles))

            remark = remark_form.save(commit=False)
            remark.debate = debate
            remark.save()
            
            informed_ids = [p.id for p in new_allowed_profiles if p != profile]

            send_emails(request, informed_ids, debate_new_topic=debate)
            messages.info(request, f'Utworzono nową naradę w nowym temacie!')
            return redirect('debates:debate', topic_id=topic.id,
                            debate_id=debate.id)
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


@query_debugger
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
            
            new_allowed_profiles = debate_form.cleaned_data['allowed_profiles']
            debate.allowed_profiles.add(*list(new_allowed_profiles))
            debate.followers.add(*list(new_allowed_profiles))

            remark = remark_form.save(commit=False)
            remark.debate = debate
            remark.save()
            
            informed_ids = [p.id for p in new_allowed_profiles if p != profile]

            send_emails(request, informed_ids, debate_new=debate)
            messages.info(request, f'Utworzono nową naradę!')
            return redirect('debates:debate', topic_id=topic_id,
                            debate_id=debate.id)
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
    if profile in topic.allowed_profiles.all() or profile.status == 'gm':
        return render(request, 'debates/create_debate.html', context)
    else:
        return redirect('home:dupa')


@query_debugger
@login_required
def debate_view(request, topic_id, debate_id):
    profile = request.user.profile
    topic = get_object_or_404(Topic, id=topic_id)
    debate = get_object_or_404(Debate, id=debate_id)
    
    debate_allowed_profiles = debate.allowed_profiles.exclude(status='gm')
    debate_followers = debate.followers.exclude(status='gm')
    remarks = debate.remarks.all().select_related('author__profile')

    last_remark = None
    last_remark_seen_by_imgs = []
    if debate.remarks.exclude(author__profile__status='gm'):
        last_remark = debate.remarks.order_by('-date_posted') \
            .prefetch_related('seen_by')[0]
        if not debate.is_ended:
            seen_by = last_remark.seen_by.all()
            if profile not in seen_by:
                last_remark.seen_by.add(profile)
            last_remark_seen_by_imgs = [
                p.image for p in last_remark.seen_by.all()
            ]

    # INFORM FORM
    # dict(request.POST).items() == < QueryDict: {
    #     'csrfmiddlewaretoken': ['KcoYDwb7r86Ll2SdQUNrDCKs...'],
    #     '2': ['on'],
    #     'debate': ['']
    # } >
    if request.method == 'POST' and 'debate' in request.POST:
        data = dict(request.POST)
        informed_ids = [k for k, v_list in data.items() if 'on' in v_list]
        debate.allowed_profiles.add(*informed_ids)
        debate.followers.add(*informed_ids)
        
        send_emails(request, informed_ids, debate_info=debate)
        messages.info(request, f'Wybrane postaci zostały dodane do narady!')

    # REMARK FORM
    if request.method == 'POST' and 'debate' not in request.POST:
        form = CreateRemarkForm(request.POST, request.FILES,
                                debate_id=debate_id)
        if form.is_valid():
            remark = form.save(commit=False)
            remark.debate = debate
            remark.save()

            informed_ids = [p.id for p in debate_followers if p != profile]

            send_emails(request, informed_ids, debate_remark=debate)
            messages.info(request, f'Twój głos zabrzmiał w naradzie!')
            return redirect('debates:debate', topic_id=topic_id,
                            debate_id=debate_id)
    else:
        form = CreateRemarkForm(initial={'author': request.user},
                                debate_id=debate_id)

    context = {
        'page_title': debate.name,
        'topic': topic,
        'debate': debate,
        'debate_allowed_profiles': debate_allowed_profiles,
        'debate_followers': debate_followers,
        'remarks': remarks,
        'last_remark': last_remark,
        'last_remark_seen_by_imgs': last_remark_seen_by_imgs,
        'form': form,
    }
    if profile in debate.allowed_profiles.all() or profile.status == 'gm':
        return render(request, 'debates/debate.html', context)
    else:
        return redirect('home:dupa')


@query_debugger
@login_required
def unfollow_debate_view(request, topic_id, debate_id):
    profile = request.user.profile
    debate = get_object_or_404(Debate, id=debate_id)
    if profile in debate.allowed_profiles.all() or profile.status == 'gm':
        debate.followers.remove(profile)
        messages.info(request, 'Przestałeś uważnie uczestniczyć w naradzie!')
        return redirect('debates:debate', topic_id=topic_id,
                        debate_id=debate_id)
    else:
        return redirect('home:dupa')


@query_debugger
@login_required
def follow_debate_view(request, topic_id, debate_id):
    profile = request.user.profile
    debate = get_object_or_404(Debate, id=debate_id)
    if profile in debate.allowed_profiles.all() or profile.status == 'gm':
        debate.followers.add(profile)
        messages.info(request, 'Od teraz uważnie uczestniczysz w naradzie!')
        return redirect('debates:debate', topic_id=topic_id,
                        debate_id=debate_id)
    else:
        return redirect('home:dupa')
