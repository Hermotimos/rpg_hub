from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Max, Q
from django.core.mail import send_mail
from django.conf import settings
from debates.models import Board, Topic
from users.models import User, Profile
from debates.forms import CreateRemarkForm, CreateTopicForm, CreateBoardForm, UpdateTopicForm


@login_required
def forum_view(request):
    queryset = Board.objects.all()

    topics_with_last_remark_date_dict = {}
    topics_with_last_active_user_dict = {}
    topics_with_remarks_by_players_count = {}

    for topic in Topic.objects.all():

        # last remark dates
        topics_with_last_remark_date_dict[topic] = topic.remarks.all().aggregate(Max('date_posted'))['date_posted__max']

        # last active users
        last_remark = topic.remarks.filter(date_posted=topics_with_last_remark_date_dict[topic])
        topics_with_last_active_user_dict[topic] = last_remark[0].author.profile.character_name if last_remark else ''

        # count of remarks by users
        cnt = 0
        for remark in topic.remarks.all():
            if remark.author not in (u for u in User.objects.all() if u.profile.character_status == 'gm'):
                cnt += 1
        topics_with_remarks_by_players_count[topic] = cnt

    boards_with_allowed_profiles_dict = {}
    for board in queryset:
        allowed_profiles = ''
        for topic in board.topics.all():
            for profile in topic.allowed_profiles.all():
                if profile.character_name not in allowed_profiles:
                    allowed_profiles += profile.character_name
        boards_with_allowed_profiles_dict[board] = allowed_profiles

    context = {
        'page_title': 'Narady',
        'queryset': queryset,
        'topics_with_last_remark_date_dict': topics_with_last_remark_date_dict,
        'topics_with_last_active_user_dict': topics_with_last_active_user_dict,
        'boards_with_allowed_profiles_dict': boards_with_allowed_profiles_dict,
        'topics_with_remarks_by_players_count': topics_with_remarks_by_players_count
    }
    return render(request, 'debates/debates_main.html', context)


@login_required
def topic_view(request, board_slug, topic_slug):
    obj = get_object_or_404(Topic, slug=topic_slug)

    allowed = ', '.join(p.character_name.split(' ', 1)[0] for p in obj.allowed_profiles.all() if p.character_status != 'gm')

    if request.method == 'POST':
        form = CreateRemarkForm(request.POST, request.FILES)
        if form.is_valid():
            remark = form.save(commit=False)
            remark.topic = obj
            remark.author = request.user
            remark.save()
            return redirect('topic', board_slug=board_slug, topic_slug=obj.slug)
    else:
        form = CreateRemarkForm()            # equals to: form = CreateRemarkForm(request.GET) - GET is the default

    context = {
        'page_title': obj.topic_name,
        'topic': obj,
        'form': form,
        'allowed': allowed
    }
    return render(request, 'debates/topic.html', context)


@login_required
def add_allowed_profiles_view(request, board_slug, topic_slug):
    obj = get_object_or_404(Topic, slug=topic_slug)

    already_allowed = obj.allowed_profiles.all()[::1]
    allowed = ', '.join(p.character_name.split(' ', 1)[0] for p in already_allowed if p.character_status != 'gm')

    if request.method == 'POST':
        form = UpdateTopicForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()

            subject = f"[RPG] Dołączenie do narady: '{obj.topic_name}'"
            message = f"{request.user.profile} dołączył Cię do narady '{obj.topic_name}' w temacie '{obj.board}'.\n" \
                      f"Uczestnicy: {', '.join(p.character_name for p in form.cleaned_data['allowed_profiles'])}\n" \
                      f"Weź udział w naradzie: {request.get_host()}/debates/{obj.board.slug}/{obj.slug}/"
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
            return redirect('topic', board_slug=board_slug, topic_slug=obj.slug)
    else:
        form = UpdateTopicForm(
            initial={
                'allowed_profiles': [p for p in Profile.objects.all() if p in obj.allowed_profiles.all()]
            }
        )

    context = {
        'page_title': 'Dodaj uczestników narady',
        'topic': obj,
        'form': form,
        'allowed': allowed
    }
    return render(request, 'debates/topic_update_users.html', context)


@login_required
def create_topic_view(request, board_slug):
    obj = Board.objects.get(slug=board_slug)

    if request.method == 'POST':
        topic_form = CreateTopicForm(request.POST or None)
        remark_form = CreateRemarkForm(request.POST, request.FILES)
        if topic_form.is_valid() and remark_form.is_valid():

            topic = topic_form.save(commit=False)
            topic.board = Board.objects.get(slug=board_slug)
            topic.starter = request.user
            topic.save()
            topic.allowed_profiles.set(topic_form.cleaned_data['allowed_profiles'])
            topic.save()

            remark = remark_form.save(commit=False)
            remark.topic = topic
            remark.author = request.user
            remark.save()

            subject = f"[RPG] Nowa narada: {topic.topic_name}"
            message = f"{request.user.profile} włączył Cię do nowej narady " \
                      f"'{topic.topic_name}' w temacie '{topic.board}'.\n" \
                      f"Uczestnicy: {', '.join(p.character_name for p in topic.allowed_profiles.all())}\n" \
                      f"Weź udział w naradzie: {request.get_host()}/debates/{topic.board.slug}/{topic.slug}/"
            sender = settings.EMAIL_HOST_USER
            receivers_list = []
            for user in User.objects.all():
                if user.profile in topic.allowed_profiles.all():
                    receivers_list.append(user.email)
            if request.user.profile.character_status != 'gm':
                receivers_list.append('lukas.kozicki@gmail.com')
            send_mail(subject, message, sender, receivers_list)

            messages.info(request, f'Utworzono nową naradę!')
            return redirect('topic', board_slug=board_slug, topic_slug=topic.slug)
    else:
        topic_form = CreateTopicForm()            # equals to: form = CreateTopicForm(request.GET) - GET is the default
        remark_form = CreateRemarkForm()

    context = {
        'page_title': 'Nowa narada',
        'topic_form': topic_form,
        'remark_form': remark_form,
        'board': obj
    }
    return render(request, 'debates/create_topic.html', context)


@login_required
def create_board_view(request):
    if request.method == 'POST':
        form = CreateBoardForm(request.POST or None)
        if form.is_valid():
            board = form.save()
            messages.info(request, f'Utworzono nowy temat narad!')
            return redirect('create-topic', board_slug=board.slug)
    else:
        form = CreateBoardForm()             # equals to: form = CreateBoardForm(request.GET) - GET is the default

    context = {
        'page_title': 'Nowy temat narad',
        'form': form,
    }
    return render(request, 'debates/create_board.html', context)
