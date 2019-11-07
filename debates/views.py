from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404

from debates.forms import CreateRemarkForm, CreateDebateForm, CreateTopicForm, InviteForm
from debates.models import Topic, Debate
from rpg_project.utils import query_debugger
from users.models import User, Profile


@query_debugger
@login_required
def debates_main_view(request):
    if request.user.profile.character_status == 'gm':
        topics = Topic.objects.all().prefetch_related('debates')
        topics_with_debates_dict = {}
        for topic in topics:
            topics_with_debates_dict[topic] = [d for d in topic.debates.all()]
    else:
        topics = Topic.objects.filter(debates__allowed_profiles=request.user.profile).prefetch_related('debates')
        topics_with_debates_dict = {}
        for topic in topics:
            topics_with_debates_dict[topic] = [d for d in topic.debates.filter(allowed_profiles=request.user.profile)]

    context = {
        'page_title': 'Narady',
        'topics': topics,
        'topics_with_debates_dict': topics_with_debates_dict
    }
    return render(request, 'debates/main.html', context)


@query_debugger
@login_required
def create_topic_view(request):
    if request.method == 'POST':
        topic_form = CreateTopicForm(request.POST)
        debate_form = CreateDebateForm(authenticated_user=request.user, data=request.POST)
        remark_form = CreateRemarkForm(request.POST, request.FILES)

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
            for profile in debate.allowed_profiles.all():
                if profile.user != request.user:
                    receivers.append(profile.user.email)
            if request.user.profile.character_status != 'gm':
                receivers.append('lukas.kozicki@gmail.com')
            send_mail(subject, message, sender, receivers)

            messages.info(request, f'Utworzono nową naradę w nowym temacie!')
            return redirect('debates:debate', topic_id=topic.id, debate_id=debate.id)
    else:
        topic_form = CreateTopicForm()
        debate_form = CreateDebateForm(authenticated_user=request.user)
        remark_form = CreateRemarkForm(initial={'author': request.user})

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
    topic = get_object_or_404(Topic, id=topic_id)

    if request.method == 'POST':
        debate_form = CreateDebateForm(authenticated_user=request.user, data=request.POST)
        remark_form = CreateRemarkForm(request.POST, request.FILES)
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
            for profile in debate.allowed_profiles.all():
                if profile.user != request.user:
                    receivers.append(profile.user.email)
            if request.user.profile.character_status != 'gm':
                receivers.append('lukas.kozicki@gmail.com')
            send_mail(subject, message, sender, receivers)

            messages.info(request, f'Utworzono nową naradę!')
            return redirect('debates:debate', topic_id=topic_id, debate_id=debate.id)
    else:
        debate_form = CreateDebateForm(authenticated_user=request.user)
        remark_form = CreateRemarkForm(initial={'author': request.user})

    context = {
        'page_title': 'Nowa narada',
        'debate_form': debate_form,
        'remark_form': remark_form,
        'topic': topic
    }
    if request.user.profile in topic.allowed_list() or request.user.profile.character_status == 'gm':
        return render(request, 'debates/create_debate.html', context)
    else:
        return redirect('home:dupa')


@query_debugger
@login_required
def debate_view(request, topic_id, debate_id):
    topic = get_object_or_404(Topic, id=topic_id)
    debate = get_object_or_404(Debate, id=debate_id)

    last_remark = debate.last_remark()
    last_remark_seen_by_imgs = ()
    if last_remark:
        profile = request.user.profile
        seen_by = last_remark.seen_by.all()
        if profile not in seen_by:
            last_remark.seen_by.add(profile)
            # new_seen = profile
            # seen_by |= Profile.objects.filter(id=new_seen.id)
            # last_remark.seen_by.set(seen_by)
        last_remark_seen_by_imgs = (p.image for p in last_remark.seen_by.all())

    allowed_str = ', '.join(p.character_name.split(' ', 1)[0]
                            for p in debate.allowed_profiles.all()
                            if p.character_status != 'gm')
    followers_str = ', '.join(p.character_name.split(' ', 1)[0]
                              for p in debate.followers.all()
                              if p.character_status != 'gm')

    if request.method == 'POST':
        form = CreateRemarkForm(request.POST, request.FILES)
        if form.is_valid():
            remark = form.save(commit=False)
            remark.debate = debate
            remark.save()

            subject = f"[RPG] Głos w naradzie: '{debate.name[:30]}...'"
            message = f"{remark.author.profile} zabrał/a głos w naradzie '{debate.name}':\n" \
                      f"'{remark.text}'\n\n" \
                      f"Weź udział w naradzie: {request.get_host()}/debates/topic:{debate.topic.id}/debate:{debate.id}/"
            sender = settings.EMAIL_HOST_USER
            receivers = []
            for user in User.objects.all():
                if user.profile in debate.followers.all() and user != request.user:
                    receivers.append(user.email)
            if request.user.profile.character_status != 'gm':
                receivers.append('lukas.kozicki@gmail.com')
            send_mail(subject, message, sender, receivers)

            messages.info(request, f'Twój głos zabrzmiał w naradzie!')
            return redirect('debates:debate', topic_id=topic_id, debate_id=debate_id)

    else:
        form = CreateRemarkForm(initial={'author': request.user})

    context = {
        'page_title': debate.name,
        'topic': topic,
        'debate': debate,
        'allowed': allowed_str,
        'followers': followers_str,
        'last_remark': last_remark,
        'last_remark_seen_by_imgs': last_remark_seen_by_imgs,
        'form': form,
    }
    if request.user.profile in debate.allowed_profiles.all() or request.user.profile.character_status == 'gm':
        return render(request, 'debates/debate.html', context)
    else:
        return redirect('home:dupa')


@query_debugger
@login_required
def debates_invite_view(request, topic_id, debate_id):
    debate = get_object_or_404(Debate, id=debate_id)

    allowed_profiles_old = debate.allowed_profiles.all()
    # followers_old = debate.followers.all()

    allowed_profiles_old_ids = [p.id for p in allowed_profiles_old]
    allowed_profiles_old_str = ', '.join(p.character_name.split(' ', 1)[0]
                                         for p in allowed_profiles_old
                                         if p.character_status != 'gm')

    if request.method == 'POST':
        form = InviteForm(authenticated_user=request.user,
                          already_allowed_profiles_ids=allowed_profiles_old_ids,
                          data=request.POST,
                          instance=debate)
        if form.is_valid():
            # debate = form.save()

            allowed_profiles_new = form.cleaned_data['allowed_profiles']
            debate.allowed_profiles.add(*list(allowed_profiles_new))
            debate.followers.add(*list(allowed_profiles_new))

            # new_followers_ids = [p.id for p in allowed_profiles_new if p not in allowed_profiles_old]
            # new_followers = followers_old
            # new_followers |= Profile.objects.filter(id__in=new_followers_ids)
            # debate.followers.set(new_followers)

            subject = f"[RPG] Dołączenie do narady: '{debate.name}'"
            message = f"{request.user.profile} dołączył/a Cię do narady '{debate.name}' w temacie '{debate.topic}'.\n"\
                      f"Uczestnicy: {', '.join(p.character_name for p in allowed_profiles_new if p.character_status != 'gm')}\n" \
                      f"Weź udział w naradzie: {request.get_host()}/debates/topic:{debate.topic.id}/debate:{debate.id}/"
            sender = settings.EMAIL_HOST_USER
            receivers = []
            for profile in debate.allowed_profiles.all():
                # exclude previously allowed users from mailing to avoid spam
                if profile not in allowed_profiles_old:
                    receivers.append(profile.user.email)
            if request.user.profile.character_status != 'gm':
                receivers.append('lukas.kozicki@gmail.com')
            send_mail(subject, message, sender, receivers)

            messages.info(request, f'Wybrane postaci zostały dodane do narady!')
            return redirect('debates:debate', topic_id=topic_id, debate_id=debate_id)
    else:
        form = InviteForm(authenticated_user=request.user,
                          already_allowed_profiles_ids=allowed_profiles_old_ids)

    context = {
        'page_title': 'Dodaj uczestników narady',
        'debate': debate,
        'form': form,
        'allowed': allowed_profiles_old_str,
    }
    if request.user.profile in debate.allowed_profiles.all() or request.user.profile.character_status == 'gm':
        return render(request, 'debates/invite.html', context)
    else:
        return redirect('home:dupa')


@query_debugger
@login_required
def unfollow_debate_view(request, topic_id, debate_id):
    debate = get_object_or_404(Debate, id=debate_id)
    if request.user.profile in debate.allowed_profiles.all() or request.user.profile.character_status == 'gm':
        # TODO: remove the above if debate.followers.remove(request.user.profile) works
        # updated_followers = debate.followers.exclude(user=request.user)
        debate.followers.remove(request.user.profile)
        messages.info(request, 'Przestałeś uważnie uczestniczyć w naradzie!')
        return redirect('debates:debate', topic_id=topic_id, debate_id=debate_id)
    else:
        return redirect('home:dupa')


@query_debugger
@login_required
def follow_debate_view(request, topic_id, debate_id):
    debate = get_object_or_404(Debate, id=debate_id)
    if request.user.profile in debate.allowed_profiles.all() or request.user.profile.character_status == 'gm':
        # TODO: remove the above if debate.followers.add(request.user.profile) works
        # followers = debate.followers.all()
        # new_follower = request.user.profile
        # followers |= Profile.objects.filter(id=new_follower.id)
        debate.followers.add(request.user.profile)
        messages.info(request, 'Od teraz uważnie uczestniczysz w naradzie!')
        return redirect('debates:debate', topic_id=topic_id, debate_id=debate_id)
    else:
        return redirect('home:dupa')
