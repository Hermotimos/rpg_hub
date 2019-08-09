from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from debates.models import Topic, Debate
from users.models import User, Profile
from debates.forms import CreateRemarkForm, CreateDebateForm, CreateTopicForm, UpdateDebateForm


@login_required
def debates_main_view(request):
    queryset = Topic.objects.all()
    context = {
        'page_title': 'Narady',
        'queryset': queryset,
    }
    return render(request, 'debates/main.html', context)


@login_required
def debate_view(request, topic_id, debate_id):
    topic = get_object_or_404(Topic, id=topic_id)
    debate = get_object_or_404(Debate, id=debate_id)

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
            remark.author = request.user
            remark.save()

            subject = f"[RPG] Głos w naradzie: '{debate.title[:30]}...'"
            message = f"{request.user.profile} zabrał/a głos w naradzie '{debate.title}':\n" \
                      f"'{remark.text}'\n\n" \
                      f"Weź udział w naradzie: {request.get_host()}/debates/topic:{debate.topic.id}/debate:{debate.id}/"
            sender = settings.EMAIL_HOST_USER
            receivers_list = []
            for user in User.objects.all():
                if user.profile in debate.followers.all() and user != request.user:
                    receivers_list.append(user.email)
            if request.user.profile.character_status != 'gm':
                receivers_list.append('lukas.kozicki@gmail.com')
            send_mail(subject, message, sender, receivers_list)

            messages.info(request, f'Twój głos zabrzmiał w naradzie!')
            return redirect('debates:debate', topic_id=topic_id, debate_id=debate_id)
    else:
        form = CreateRemarkForm()            # equals to: form = CreateRemarkForm(request.GET) - GET is the default

    context = {
        'page_title': debate.title,
        'topic': topic,
        'debate': debate,
        'form': form,
        'allowed': allowed_str,
        'followers': followers_str
    }
    return render(request, 'debates/debate.html', context)


@login_required
def add_allowed_profiles_view(request, topic_id, debate_id):
    debate = get_object_or_404(Debate, id=debate_id)

    old_allowed_profiles = debate.allowed_profiles.all()[::1]
    old_allowed_profiles_ids = [p.id for p in old_allowed_profiles]
    allowed_str = ', '.join(p.character_name.split(' ', 1)[0]
                            for p in old_allowed_profiles
                            if p.character_status != 'gm')
    old_followers = debate.followers.all()

    if request.method == 'POST':
        form = UpdateDebateForm(authenticated_user=request.user,
                                already_allowed_profiles_ids=old_allowed_profiles_ids,
                                data=request.POST, instance=debate)
        if form.is_valid():
            debate = form.save()

            allowed_profiles = form.cleaned_data['allowed_profiles']
            allowed_profiles |= Profile.objects.filter(id=request.user.id)
            allowed_profiles |= Profile.objects.filter(id__in=old_allowed_profiles_ids)
            debate.allowed_profiles.set(allowed_profiles)

            new_followers_ids = [p.id for p in allowed_profiles if p not in old_allowed_profiles]
            new_followers = old_followers
            new_followers |= Profile.objects.filter(id__in=new_followers_ids)
            debate.followers.set(new_followers)

            subject = f"[RPG] Dołączenie do narady: '{debate.title}'"
            message = f"{request.user.profile} dołączył/a Cię do narady '{debate.title}' w temacie '{debate.topic}'.\n"\
                      f"Uczestnicy: {', '.join(p.character_name for p in allowed_profiles if p.character_status != 'gm')}\n" \
                      f"Weź udział w naradzie: {request.get_host()}/debates/topic:{debate.topic.id}/debate:{debate.id}/"
            sender = settings.EMAIL_HOST_USER
            receivers_list = []
            for profile in debate.allowed_profiles.all():
                if profile not in old_allowed_profiles:
                    receivers_list.append(profile.user.email)
            if request.user.profile.character_status != 'gm':
                receivers_list.append('lukas.kozicki@gmail.com')
            send_mail(subject, message, sender, receivers_list)

            messages.info(request, f'Wybrane postaci zostały dodane do narady!')
            return redirect('debates:debate', topic_id=topic_id, debate_id=debate_id)
    else:
        form = UpdateDebateForm(authenticated_user=request.user,
                                already_allowed_profiles_ids=old_allowed_profiles_ids)

    context = {
        'page_title': 'Dodaj uczestników narady',
        'debate': debate,
        'form': form,
        'allowed': allowed_str
    }
    return render(request, 'debates/invite.html', context)


@login_required
def create_debate_view(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)

    if request.method == 'POST':
        debate_form = CreateDebateForm(authenticated_user=request.user, data=request.POST or None)
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
            remark.author = request.user
            remark.save()

            subject = f"[RPG] Nowa narada: {debate.title}"
            message = f"{request.user.profile} włączył/a Cię do nowej narady " \
                      f"'{debate.title}' w temacie '{debate.topic}'.\n" \
                      f"Uczestnicy: {', '.join(p.character_name for p in debate.allowed_profiles.all())}\n" \
                      f"Weź udział w naradzie: {request.get_host()}/debates/topic:{debate.topic.id}/debate:{debate.id}/"
            sender = settings.EMAIL_HOST_USER
            receivers_list = []
            for user in User.objects.all():
                if user.profile in debate.allowed_profiles.all() and user != request.user:
                    receivers_list.append(user.email)
            if request.user.profile.character_status != 'gm':
                receivers_list.append('lukas.kozicki@gmail.com')
            send_mail(subject, message, sender, receivers_list)

            messages.info(request, f'Utworzono nową naradę!')
            return redirect('debates:debate', topic_id=topic_id, debate_id=debate.id)
    else:
        debate_form = CreateDebateForm(authenticated_user=request.user)
        remark_form = CreateRemarkForm()

    context = {
        'page_title': 'Nowa narada',
        'debate_form': debate_form,
        'remark_form': remark_form,
        'topic': topic
    }
    return render(request, 'debates/create_debate.html', context)


@login_required
def create_topic_view(request):
    if request.method == 'POST':
        form = CreateTopicForm(request.POST or None)
        if form.is_valid():
            topic = form.save()
            messages.info(request, f'Utworzono nowy temat narad!')
            return redirect('debates:create-debate', topic_id=topic.id)
    else:
        form = CreateTopicForm()             # equals to: form = CreateTopicForm(request.GET) - GET is the default

    context = {
        'page_title': 'Nowy temat narad',
        'form': form,
    }
    return render(request, 'debates/create_topic.html', context)


@login_required
def unfollow_debate_view(request, topic_id, debate_id):
    obj = Debate.objects.get(id=debate_id)
    updated_followers = obj.followers.exclude(user=request.user)
    obj.followers.set(updated_followers)
    messages.info(request, 'Przestałeś uważnie uczestniczyć w naradzie!')
    return redirect('debates:debate', topic_id=topic_id, debate_id=debate_id)


@login_required
def follow_debate_view(request, topic_id, debate_id):
    obj = Debate.objects.get(id=debate_id)
    followers = obj.followers.all()
    new_follower = request.user.profile
    followers |= Profile.objects.filter(id=new_follower.id)
    obj.followers.set(followers)
    messages.info(request, 'Od teraz uważnie uczestniczysz w naradzie!')
    return redirect('debates:debate', topic_id=topic_id, debate_id=debate_id)
