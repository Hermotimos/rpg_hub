from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Max
from django.core.mail import send_mail
from django.conf import settings
from debates.models import Topic, Debate
from users.models import User, Profile
from debates.forms import CreateRemarkForm, CreateDebateForm, CreateTopicForm, UpdateDebateForm


@login_required
def debates_main_view(request):
    queryset = Topic.objects.all()

    debates_with_last_remark_date_dict = {}
    debates_with_last_active_user_dict = {}
    debates_with_remarks_by_players_count = {}

    for debate in Debate.objects.all():

        # last remark dates
        debates_with_last_remark_date_dict[debate] = debate.remarks.all().aggregate(Max('date_posted'))['date_posted__max']

        # last active users
        last_remark = debate.remarks.filter(date_posted=debates_with_last_remark_date_dict[debate])
        debates_with_last_active_user_dict[debate] = last_remark[0].author.profile.character_name if last_remark else ''

        # count of remarks by users
        cnt = 0
        for remark in debate.remarks.all():
            if remark.author not in (u for u in User.objects.all() if u.profile.character_status == 'gm'):
                cnt += 1
        debates_with_remarks_by_players_count[debate] = cnt

    topics_with_allowed_profiles_dict = {}
    for topic in queryset:
        allowed_profiles = ''
        for debate in topic.debates.all():
            for profile in debate.allowed_profiles.all():
                if profile.character_name not in allowed_profiles:
                    allowed_profiles += profile.character_name
        topics_with_allowed_profiles_dict[topic] = allowed_profiles

    context = {
        'page_title': 'Narady',
        'queryset': queryset,
        'debates_with_last_remark_date_dict': debates_with_last_remark_date_dict,
        'debates_with_last_active_user_dict': debates_with_last_active_user_dict,
        'topics_with_allowed_profiles_dict': topics_with_allowed_profiles_dict,
        'debates_with_remarks_by_players_count': debates_with_remarks_by_players_count
    }
    return render(request, 'debates/debates_main.html', context)


@login_required
def debate_view(request, topic_slug, debate_slug):
    obj = get_object_or_404(Debate, slug=debate_slug)

    allowed = ', '.join(p.character_name.split(' ', 1)[0] for p in obj.allowed_profiles.all() if p.character_status != 'gm')

    if request.method == 'POST':
        form = CreateRemarkForm(request.POST, request.FILES)
        if form.is_valid():
            remark = form.save(commit=False)
            remark.debate = obj
            remark.author = request.user
            remark.save()
            return redirect('debate', topic_slug=topic_slug, debate_slug=obj.slug)
    else:
        form = CreateRemarkForm()            # equals to: form = CreateRemarkForm(request.GET) - GET is the default

    context = {
        'page_title': obj.title,
        'debate': obj,
        'form': form,
        'allowed': allowed
    }
    return render(request, 'debates/debate.html', context)


@login_required
def add_allowed_profiles_view(request, topic_slug, debate_slug):
    obj = get_object_or_404(Debate, slug=debate_slug)

    already_allowed = obj.allowed_profiles.all()[::1]
    allowed = ', '.join(p.character_name.split(' ', 1)[0] for p in already_allowed if p.character_status != 'gm')

    if request.method == 'POST':
        form = UpdateDebateForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()

            subject = f"[RPG] Dołączenie do narady: '{obj.title}'"
            message = f"{request.user.profile} dołączył Cię do narady '{obj.title}' w temacie '{obj.topic}'.\n" \
                      f"Uczestnicy: {', '.join(p.character_name for p in form.cleaned_data['allowed_profiles'])}\n" \
                      f"Weź udział w naradzie: {request.get_host()}/debates/{obj.topic.slug}/{obj.slug}/"
            sender = settings.EMAIL_HOST_USER
            receivers_list = []

            newly_allowed = [p for p in form.cleaned_data['allowed_profiles'] if p not in already_allowed]
            for profile in newly_allowed:
                if profile.user.email:
                    receivers_list.append(profile.user.email)
            if request.user.profile.character_status != 'gm':
                receivers_list.append('lukas.kozicki@gmail.com')
            send_mail(subject, message, sender, receivers_list)

            messages.info(request, f'Wybrane postaci zostały dodane do narady!')
            return redirect('debate', topic_slug=topic_slug, debate_slug=obj.slug)
    else:
        form = UpdateDebateForm(
            initial={
                'allowed_profiles': [p for p in Profile.objects.all() if p in obj.allowed_profiles.all()]
            }
        )

    context = {
        'page_title': 'Dodaj uczestników narady',
        'debate': obj,
        'form': form,
        'allowed': allowed
    }
    return render(request, 'debates/debate_update_users.html', context)


@login_required
def create_debate_view(request, topic_slug):
    obj = Topic.objects.get(slug=topic_slug)

    if request.method == 'POST':
        debate_form = CreateDebateForm(request.POST or None)
        remark_form = CreateRemarkForm(request.POST, request.FILES)
        if debate_form.is_valid() and remark_form.is_valid():

            debate = debate_form.save(commit=False)
            debate.topic = Topic.objects.get(slug=topic_slug)
            debate.starter = request.user
            debate.save()
            debate.allowed_profiles.set(debate_form.cleaned_data['allowed_profiles'])
            debate.save()

            remark = remark_form.save(commit=False)
            remark.debate = debate
            remark.author = request.user
            remark.save()

            subject = f"[RPG] Nowa narada: {debate.title}"
            message = f"{request.user.profile} włączył Cię do nowej narady " \
                      f"'{debate.title}' w temacie '{debate.topic}'.\n" \
                      f"Uczestnicy: {', '.join(p.character_name for p in debate.allowed_profiles.all())}\n" \
                      f"Weź udział w naradzie: {request.get_host()}/debates/{debate.topic.slug}/{debate.slug}/"
            sender = settings.EMAIL_HOST_USER
            receivers_list = []
            for user in User.objects.all():
                if user.profile in debate.allowed_profiles.all():
                    receivers_list.append(user.email)
            if request.user.profile.character_status != 'gm':
                receivers_list.append('lukas.kozicki@gmail.com')
            send_mail(subject, message, sender, receivers_list)

            messages.info(request, f'Utworzono nową naradę!')
            return redirect('debate', topic_slug=topic_slug, debate_slug=debate.slug)
    else:
        debate_form = CreateDebateForm()            # equals to: form = CreateDebateForm(request.GET) - GET is the default
        remark_form = CreateRemarkForm()

    context = {
        'page_title': 'Nowa narada',
        'debate_form': debate_form,
        'remark_form': remark_form,
        'topic': obj
    }
    return render(request, 'debates/create_debate.html', context)


@login_required
def create_topic_view(request):
    if request.method == 'POST':
        form = CreateTopicForm(request.POST or None)
        if form.is_valid():
            topic = form.save()
            messages.info(request, f'Utworzono nowy temat narad!')
            return redirect('create-debate', topic_slug=topic.slug)
    else:
        form = CreateTopicForm()             # equals to: form = CreateTopicForm(request.GET) - GET is the default

    context = {
        'page_title': 'Nowy temat narad',
        'form': form,
    }
    return render(request, 'debates/create_topic.html', context)
