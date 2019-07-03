from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Max
from django.core.mail import send_mail
from django.conf import settings
from forum.models import Board, Topic, Post
from users.models import Profile, User
from forum.forms import CreatePostForm, CreateTopicForm, CreateBoardForm, UpdateTopicForm


@login_required
def forum_view(request):
    boards_list = Board.objects.all()
    topics_list = Topic.objects.all()

    topics_with_last_post_date_dict = {topic: topic.posts.all().aggregate(Max('date_posted'))['date_posted__max']
                                       for topic in topics_list}
    topics_with_last_active_user_dict = {}
    for topic in topics_list:
        last_post = topic.posts.filter(date_posted=topics_with_last_post_date_dict[topic])
        topics_with_last_active_user_dict[topic] = last_post[0].author.profile.character_name if last_post else ''

    boards_with_allowed_profiles_dict = {}
    for board in boards_list:
        allowed_profiles = ''
        for topic in board.topics.all():
            for profile in topic.allowed_profiles.all():
                if profile.character_name not in allowed_profiles:
                    allowed_profiles += profile.character_name + ', '
        boards_with_allowed_profiles_dict[board] = allowed_profiles

    context = {
        'page_title': 'Wieczorne narady',
        'boards_list': boards_list,
        'topics_with_last_post_date_dict': topics_with_last_post_date_dict,
        'topics_with_last_active_user_dict': topics_with_last_active_user_dict,
        'boards_with_allowed_profiles_dict': boards_with_allowed_profiles_dict
    }
    return render(request, 'forum/forum.html', context)


@login_required
def posts_in_topic_view(request, board_slug, topic_slug):
    current_topic = get_object_or_404(Topic, slug=topic_slug)
    logged_user = request.user

    if request.method == 'POST':
        post_form = CreatePostForm(request.POST, request.FILES)             # TODO what is wrong ???
        if post_form.is_valid():
            post = post_form.save(commit=False)
            post.topic = current_topic
            post.author = logged_user
            post.save()
            return redirect('topic', board_slug=board_slug, topic_slug=current_topic.slug)
    else:
        post_form = CreatePostForm()            # equals to: form = CreatePostForm(request.GET) - GET is the default

    context = {
        'page_title': current_topic.topic_name,
        'topic': current_topic,
        'post_form': post_form
    }
    return render(request, 'forum/topic.html', context)


@login_required
def add_allowed_profiles_view(request, board_slug, topic_slug):
    current_topic = get_object_or_404(Topic, slug=topic_slug)

    if request.method == 'POST':
        topic_update_form = UpdateTopicForm(request.POST, instance=current_topic)
        if topic_update_form.is_valid():
            topic_update_form.save()
            return redirect('topic', board_slug=board_slug, topic_slug=current_topic.slug)
    else:
        topic_update_form = UpdateTopicForm(
            initial={
                'allowed_profiles': [p for p in Profile.objects.all() if p in current_topic.allowed_profiles.all()]
            }
        )

    context = {
        'page_title': 'Dodaj uczestników narady ' + '"' + current_topic.topic_name + '"',
        'topic': current_topic,
        'topic_update_form': topic_update_form
    }
    return render(request, 'forum/topic_update_users.html', context)


@login_required
def create_topic_view(request, board_slug):
    logged_user = request.user

    if request.method == 'POST':
        topic_form = CreateTopicForm(request.POST or None)
        if topic_form.is_valid():

            topic = topic_form.save(commit=False)
            topic.board = Board.objects.get(slug=board_slug)
            topic.starter = logged_user
            topic.save()

            allowed_profiles_cleaned = topic_form.cleaned_data['allowed_profiles']
            topic.allowed_profiles.set(allowed_profiles_cleaned)
            topic.save()

            Post.objects.create(
                text=topic_form.cleaned_data.get('first_post'),
                topic=topic,
                author=logged_user
            )

            subject = f"[RPG] Nowa narada: {topic_form.cleaned_data['topic_name']}"
            message = f"{request.user.profile} dołączył Cię do narady.\n" \
                      f"Narada '{topic.topic_name}' w temacie '{topic.board}'.\n" \
                      f"Link: http://127.0.0.1:8000/forum/{topic.board.slug}/{topic.slug}/"
            sender = settings.EMAIL_HOST_USER
            receivers_list = []
            for user in User.objects.all():
                if user.profile in topic.allowed_profiles.all():
                    receivers_list.append(user.email)
            if logged_user.profile.character_status != 'MG':
                receivers_list.append('lukas.kozicki@gmail.com')

            send_mail(subject, message, sender, receivers_list)
            return redirect('topic', board_slug=board_slug, topic_slug=topic.slug)
    else:
        topic_form = CreateTopicForm()            # equals to: form = CreateTopicForm(request.GET) - GET is the default

    context = {
        'page_title': 'Nowa narada',
        'topic_form': topic_form,
    }
    return render(request, 'forum/create_topic.html', context)


@login_required
def create_board_view(request):
    if request.method == 'POST':
        board_form = CreateBoardForm(request.POST or None)
        if board_form.is_valid():
            board = board_form.save()
            return redirect('create_topic', board_slug=board.slug)
    else:
        board_form = CreateBoardForm()             # equals to: form = CreateBoardForm(request.GET) - GET is the default

    context = {
        'page_title': 'Nowy temat',
        'board_form': board_form,
    }
    return render(request, 'forum/create_board.html', context)
