from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Max
from django.core.mail import send_mail
from django.conf import settings
from forum.models import Board, Topic
from users.models import User, Profile
from forum.forms import CreatePostForm, CreateTopicForm, CreateBoardForm, UpdateTopicForm


@login_required
def forum_view(request):
    queryset = Board.objects.all()

    topics_with_last_post_date_dict = {topic: topic.posts.all().aggregate(Max('date_posted'))['date_posted__max']
                                       for topic in Topic.objects.all()}

    topics_with_last_active_user_dict = {}
    for topic in Topic.objects.all():
        last_post = topic.posts.filter(date_posted=topics_with_last_post_date_dict[topic])
        topics_with_last_active_user_dict[topic] = last_post[0].author.profile.character_name if last_post else ''

    boards_with_allowed_profiles_dict = {}
    for board in queryset:
        allowed_profiles = ''
        for topic in board.topics.all():
            for profile in topic.allowed_profiles.all():
                if profile.character_name not in allowed_profiles:
                    allowed_profiles += profile.character_name
        boards_with_allowed_profiles_dict[board] = allowed_profiles

    context = {
        'page_title': 'Wieczorne narady',
        'queryset': queryset,
        'topics_with_last_post_date_dict': topics_with_last_post_date_dict,
        'topics_with_last_active_user_dict': topics_with_last_active_user_dict,
        'boards_with_allowed_profiles_dict': boards_with_allowed_profiles_dict
    }
    return render(request, 'forum/forum.html', context)


@login_required
def posts_in_topic_view(request, board_slug, topic_slug):
    obj = get_object_or_404(Topic, slug=topic_slug)

    allowed = ', '.join(p.character_name.split(' ', 1)[0] for p in obj.allowed_profiles.all() if p.character_status != 'gm')

    if request.method == 'POST':
        form = CreatePostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.topic = obj
            post.author = request.user
            post.save()
            return redirect('topic', board_slug=board_slug, topic_slug=obj.slug)
    else:
        form = CreatePostForm()            # equals to: form = CreatePostForm(request.GET) - GET is the default

    context = {
        'page_title': obj.topic_name,
        'topic': obj,
        'form': form,
        'allowed': allowed
    }
    return render(request, 'forum/topic.html', context)


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
                      f"Weź udział w naradzie: {request.get_host()}/forum/{obj.board.slug}/{obj.slug}/"
            sender = settings.EMAIL_HOST_USER
            receivers_list = []

            newly_allowed = [p for p in form.cleaned_data['allowed_profiles'] if p not in already_allowed]
            for profile in newly_allowed:
                if profile.user.email:
                    receivers_list.append(profile.user.email)
            if request.user.profile.character_status != 'gm':
                receivers_list.append('lukas.kozicki@gmail.com')
            send_mail(subject, message, sender, receivers_list)

            messages.success(request, f'Dodano do narady wybrane postaci!')
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
    return render(request, 'forum/topic_update_users.html', context)


@login_required
def create_topic_view(request, board_slug):
    obj = Board.objects.get(slug=board_slug)

    if request.method == 'POST':
        topic_form = CreateTopicForm(request.POST or None)
        post_form = CreatePostForm(request.POST, request.FILES)
        if topic_form.is_valid() and post_form.is_valid():

            topic = topic_form.save(commit=False)
            topic.board = Board.objects.get(slug=board_slug)
            topic.starter = request.user
            topic.save()
            topic.allowed_profiles.set(topic_form.cleaned_data['allowed_profiles'])
            topic.save()

            post = post_form.save(commit=False)
            post.topic = topic
            post.author = request.user
            post.save()

            subject = f"[RPG] Nowa narada: {topic.topic_name}"
            message = f"{request.user.profile} włączył Cię do nowej narady " \
                      f"'{topic.topic_name}' w temacie '{topic.board}'.\n" \
                      f"Uczestnicy: {', '.join(p.character_name for p in topic.allowed_profiles.all())}\n" \
                      f"Weź udział w naradzie: {request.get_host()}/forum/{topic.board.slug}/{topic.slug}/"
            sender = settings.EMAIL_HOST_USER
            receivers_list = []
            for user in User.objects.all():
                if user.profile in topic.allowed_profiles.all():
                    receivers_list.append(user.email)
            if request.user.profile.character_status != 'gm':
                receivers_list.append('lukas.kozicki@gmail.com')
            send_mail(subject, message, sender, receivers_list)

            messages.success(request, f'Utworzono nową naradę!')
            return redirect('topic', board_slug=board_slug, topic_slug=topic.slug)
    else:
        topic_form = CreateTopicForm()            # equals to: form = CreateTopicForm(request.GET) - GET is the default
        post_form = CreatePostForm()

    context = {
        'page_title': 'Nowa narada',
        'topic_form': topic_form,
        'post_form': post_form,
        'board': obj
    }
    return render(request, 'forum/create_topic.html', context)


@login_required
def create_board_view(request):
    if request.method == 'POST':
        form = CreateBoardForm(request.POST or None)
        if form.is_valid():
            board = form.save()
            messages.success(request, f'Utworzono nowy temat narad!')
            return redirect('create_topic', board_slug=board.slug)
    else:
        form = CreateBoardForm()             # equals to: form = CreateBoardForm(request.GET) - GET is the default

    context = {
        'page_title': 'Nowy temat narad',
        'form': form,
    }
    return render(request, 'forum/create_board.html', context)
