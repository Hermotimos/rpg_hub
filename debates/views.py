from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db.models import Count, Case, When, IntegerField, Max, Min, Prefetch, Q
from django.shortcuts import render, redirect, get_object_or_404

from debates.forms import CreateRemarkForm, CreateDebateForm, CreateTopicForm, InviteForm
from debates.models import Topic, Debate
from rpg_project.utils import query_debugger
from users.models import User, Profile


@query_debugger
@login_required
def debates_main_view(request):
    profile = request.user.profile
    if profile.character_status == 'gm':
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
                        When(~Q(remarks__author__profile__character_status='gm'), then=1),
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
        debate_form = CreateDebateForm(authenticated_user=request.user, data=request.POST)
        remark_form = CreateRemarkForm(request.POST, request.FILES, debate_id=0)

        if topic_form.is_valid() and debate_form.is_valid() and remark_form.is_valid():
            topic = topic_form.save()

            debate = debate_form.save(commit=False)
            debate.topic = topic
            debate.starter = request.user
            debate.save()
            allowed_profiles = debate_form.cleaned_data['allowed_profiles']
            allowed_profiles |= Profile.objects.filter(id=request.user.id)
            debate.allowed_profiles.set(allowed_profiles)
            debate.followers.set(allowed_profiles)

            remark = remark_form.save(commit=False)
            remark.debate = debate
            remark.save()

            subject = f"[RPG] Nowa narada w nowym temacie: {debate.name}"
            message = f"{remark.author.profile} włączył/a Cię do nowej narady " \
                f"'{debate.name}' w temacie '{debate.topic}'.\n" \
                f"Uczestnicy: {', '.join(p.character_name for p in debate.allowed_profiles.all())}\n" \
                f"Weź udział w naradzie: {request.get_host()}/debates/topic:{debate.topic.id}/debate:{debate.id}/"
            sender = settings.EMAIL_HOST_USER
            receivers = []
            for profile in allowed_profiles:
                if profile.user != request.user:
                    receivers.append(profile.user.email)
            if profile.character_status != 'gm':
                receivers.append('lukas.kozicki@gmail.com')
            send_mail(subject, message, sender, receivers)

            messages.info(request, f'Utworzono nową naradę w nowym temacie!')
            return redirect('debates:debate', topic_id=topic.id, debate_id=debate.id)
    else:
        topic_form = CreateTopicForm()
        debate_form = CreateDebateForm(authenticated_user=request.user)
        remark_form = CreateRemarkForm(initial={'author': request.user}, debate_id=0)

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
        debate_form = CreateDebateForm(authenticated_user=request.user, data=request.POST)
        remark_form = CreateRemarkForm(request.POST, request.FILES, debate_id=0)
        if debate_form.is_valid() and remark_form.is_valid():

            debate = debate_form.save(commit=False)
            debate.topic = Topic.objects.get(id=topic_id)
            debate.starter = request.user
            debate.save()
            allowed_profiles = debate_form.cleaned_data['allowed_profiles']
            allowed_profiles |= Profile.objects.filter(id=request.user.id)
            debate.allowed_profiles.set(allowed_profiles)
            debate.followers.set(allowed_profiles)

            remark = remark_form.save(commit=False)
            remark.debate = debate
            remark.save()

            subject = f"[RPG] Nowa narada: {debate.name}"
            message = f"{remark.author.profile} włączył/a Cię do nowej narady " \
                      f"'{debate.name}' w temacie '{debate.topic}'.\n" \
                      f"Uczestnicy: {', '.join(p.character_name for p in debate.allowed_profiles.all())}\n" \
                      f"Weź udział w naradzie: {request.get_host()}/debates/topic:{debate.topic.id}/debate:{debate.id}/"
            sender = settings.EMAIL_HOST_USER
            receivers = []
            for p in allowed_profiles:
                if p != request.user.profile:
                    receivers.append(p.user.email)
            if profile.character_status != 'gm':
                receivers.append('lukas.kozicki@gmail.com')
            send_mail(subject, message, sender, receivers)

            messages.info(request, f'Utworzono nową naradę!')
            return redirect('debates:debate', topic_id=topic_id, debate_id=debate.id)
    else:
        debate_form = CreateDebateForm(authenticated_user=request.user)
        remark_form = CreateRemarkForm(initial={'author': request.user}, debate_id=0)

    context = {
        'page_title': 'Nowa narada',
        'debate_form': debate_form,
        'remark_form': remark_form,
        'topic': topic
    }
    if profile in topic.allowed_profiles.all() or profile.character_status == 'gm':
        return render(request, 'debates/create_debate.html', context)
    else:
        return redirect('home:dupa')


@query_debugger
@login_required
def debate_view(request, topic_id, debate_id):
    profile = request.user.profile
    topic = get_object_or_404(Topic, id=topic_id)
    debate = get_object_or_404(Debate, id=debate_id)

    debate_allowed_profiles = debate.allowed_profiles.all()
    debate_followers = debate.followers.all()
    remarks = debate.remarks.all().select_related('author__profile')
    last_remark = debate.remarks.order_by('-date_posted')[0]

    last_remark_seen_by_imgs = ()
    if not debate.is_ended:
        seen_by = last_remark.seen_by.all()
        if profile not in seen_by:
            last_remark.seen_by.add(profile)
        last_remark_seen_by_imgs = (p.image for p in last_remark.seen_by.all())

    if request.method == 'POST':
        form = CreateRemarkForm(request.POST, request.FILES, debate_id=debate_id)
        if form.is_valid():
            remark = form.save(commit=False)
            remark.debate = debate
            remark.save()

            subject = f"[RPG] Głos w naradzie: '{debate.name[:30]}...'"
            message = f"{remark.author.profile} zabrał/a głos w naradzie '{debate.name}':\n" \
                      f"'{remark.text}'\n\n" \
                      f"Weź udział w naradzie: {request.get_host()}/debates/topic:{topic.id}/debate:{debate.id}/"
            sender = settings.EMAIL_HOST_USER
            receivers = []
            for user in User.objects.all():
                if user.profile in debate.followers.all() and user != request.user:
                    receivers.append(user.email)
            if profile.character_status != 'gm':
                receivers.append('lukas.kozicki@gmail.com')
            send_mail(subject, message, sender, receivers)

            messages.info(request, f'Twój głos zabrzmiał w naradzie!')
            return redirect('debates:debate', topic_id=topic_id, debate_id=debate_id)

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
    if profile in debate.allowed_profiles.all() or profile.character_status == 'gm':
        return render(request, 'debates/debate.html', context)
    else:
        return redirect('home:dupa')


@query_debugger
@login_required
def debates_invite_view(request, topic_id, debate_id):
    profile = request.user.profile
    debate = get_object_or_404(Debate, id=debate_id)

    allowed_profiles_old = debate.allowed_profiles.all()

    if request.method == 'POST':
        form = InviteForm(authenticated_user=request.user,
                          already_allowed_profiles=allowed_profiles_old,
                          data=request.POST,
                          instance=debate)
        if form.is_valid():
            allowed_profiles_new = form.cleaned_data['allowed_profiles']
            debate.allowed_profiles.add(*list(allowed_profiles_new))
            debate.followers.add(*list(allowed_profiles_new))

            subject = f"[RPG] Dołączenie do narady: '{debate.name}'"
            message = f"{profile} dołączył/a Cię do narady '{debate.name}' w temacie '{debate.topic}'.\n"\
                      f"Uczestnicy: {', '.join(p.character_name for p in allowed_profiles_new if p.character_status != 'gm')}\n" \
                      f"Weź udział w naradzie: {request.get_host()}/debates/topic:{debate.topic.id}/debate:{debate.id}/"
            sender = settings.EMAIL_HOST_USER
            receivers = []
            for p in allowed_profiles_new:
                receivers.append(p.user.email)
            if profile.character_status != 'gm':
                receivers.append('lukas.kozicki@gmail.com')
            send_mail(subject, message, sender, receivers)

            messages.info(request, f'Wybrane postaci zostały dodane do narady!')
            return redirect('debates:debate', topic_id=topic_id, debate_id=debate_id)
    else:
        form = InviteForm(authenticated_user=request.user,
                          already_allowed_profiles=allowed_profiles_old)

    context = {
        'page_title': 'Dodaj uczestników narady',
        'debate': debate,
        'debate_allowed_profiles': allowed_profiles_old,
        'form': form,
    }
    if profile in debate.allowed_profiles.all() or profile.character_status == 'gm':
        return render(request, 'debates/invite.html', context)
    else:
        return redirect('home:dupa')


@query_debugger
@login_required
def unfollow_debate_view(request, topic_id, debate_id):
    profile = request.user.profile
    debate = get_object_or_404(Debate, id=debate_id)
    if profile in debate.allowed_profiles.all() or profile.character_status == 'gm':
        debate.followers.remove(profile)
        messages.info(request, 'Przestałeś uważnie uczestniczyć w naradzie!')
        return redirect('debates:debate', topic_id=topic_id, debate_id=debate_id)
    else:
        return redirect('home:dupa')


@query_debugger
@login_required
def follow_debate_view(request, topic_id, debate_id):
    profile = request.user.profile
    debate = get_object_or_404(Debate, id=debate_id)
    if profile in debate.allowed_profiles.all() or profile.character_status == 'gm':
        debate.followers.add(profile)
        messages.info(request, 'Od teraz uważnie uczestniczysz w naradzie!')
        return redirect('debates:debate', topic_id=topic_id, debate_id=debate_id)
    else:
        return redirect('home:dupa')
