from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Max, Min, Sum
from .models import Board, Topic, Post, User
from .forms import CreatePostForm, CreateTopicForm


def forum_view(request):
    boards_list = Board.objects.all()
    topics_list = Topic.objects.all()

    # dict comprehension
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


def posts_in_topic_view(request, board_slug, topic_slug):
    board = get_object_or_404(Board, slug=board_slug)
    topic = get_object_or_404(Topic, slug=topic_slug)

    context = {
        'board': board,
        'topic': topic,
        'page_title': topic.topic_name,
        'topic_posts_list': topic.posts.all(),
    }
    return render(request, 'forum/topic.html', context)


def create_topic_view(request, board_slug):
    board = get_object_or_404(Board, slug=board_slug)
    logged_user = User.objects.first()                 # TODO get currently logged in user (now it's just first one)

    if request.method == 'POST':
        form = CreateTopicForm(request.POST or None)       # needs way to set author=authenticated user
        if form.is_valid():
            topic = form.save(commit=False)
            topic.board = board
            topic.starter = logged_user
            topic.save()

            Post.objects.create(
                text=form.cleaned_data.get('first_post'),
                topic=topic,
                author=logged_user
            )
            return redirect('topic', board_slug=board.slug, topic_slug=topic.slug)
    else:
        form = CreateTopicForm()

    context = {
        'topic': form,
        'board': form
    }
    return render(request, 'forum/create_topic.html', context)


def create_post_view(request):
    post = CreatePostForm()     # equals to: post = CreatePostForm(request.GET)  ==> because GET is the default method
    # post = CreatePostForm(request.POST or None)       # needs way to set author=authenticated user
    if post.is_valid():
        post.save()
        post = CreatePostForm()

    context = {
        'post': post
    }
    return render(request, 'forum/create_post.html', context)


