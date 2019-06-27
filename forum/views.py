from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Max
from .models import Board, Topic, Post
from .forms import CreatePostForm, CreateTopicForm, CreateBoardForm


@login_required
def forum_view(request):
    boards_list = Board.objects.all()
    topics_list = Topic.objects.all()

    topics_with_last_post_date_dict = {topic: topic.posts.all().aggregate(Max('date_posted'))['date_posted__max']
                                       for topic in topics_list}
    topics_with_last_active_user_dict = {}
    for topic in topics_list:
        last_post = topic.posts.filter(date_posted=topics_with_last_post_date_dict[topic])
        topics_with_last_active_user_dict[topic] = last_post[0].author if last_post else ''

    context = {
        'page_title': 'Wieczorne narady',
        'boards_list': boards_list,
        'topics_with_last_post_date_dict': topics_with_last_post_date_dict,
        'topics_with_last_active_user_dict': topics_with_last_active_user_dict,
    }
    return render(request, 'forum/forum.html', context)


@login_required
def posts_in_topic_view(request, board_slug, topic_slug):
    topic = get_object_or_404(Topic, slug=topic_slug)
    logged_user = request.user

    if request.method == 'POST':
        form = CreatePostForm(request.POST or None)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.topic = topic
            new_post.author = logged_user
            new_post.save()
            return redirect('topic', board_slug=board_slug, topic_slug=topic.slug)
    else:
        form = CreatePostForm()                     # equals to: form = CreatePostForm(request.GET) - GET is the default

    context = {
        'page_title': topic.topic_name,
        'topic': topic,
        'new_post': form,
    }
    return render(request, 'forum/topic.html', context)


@login_required
def create_topic_view(request, board_slug):
    logged_user = request.user

    if request.method == 'POST':
        form = CreateTopicForm(request.POST or None)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.board = Board.objects.get(slug=board_slug)
            topic.starter = logged_user
            topic.save()

            Post.objects.create(
                text=form.cleaned_data.get('first_post'),
                topic=topic,
                author=logged_user
            )
            return redirect('topic', board_slug=board_slug, topic_slug=topic.slug)
    else:
        form = CreateTopicForm()                   # equals to: form = CreateTopicForm(request.GET) - GET is the default

    context = {
        'page_title': 'Nowa narada',
        'topic': form,
    }
    return render(request, 'forum/create_topic.html', context)


@login_required
def create_board_view(request):
    if request.method == 'POST':
        form = CreateBoardForm(request.POST or None)
        if form.is_valid():
            board = form.save()
            return redirect('create_topic', board_slug=board.slug)
    else:
        form = CreateBoardForm()                   # equals to: form = CreateBoardForm(request.GET) - GET is the default

    context = {
        'page_title': 'Nowy temat',
        'board': form,
    }
    return render(request, 'forum/create_board.html', context)
