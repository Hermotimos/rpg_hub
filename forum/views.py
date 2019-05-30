from django.http import Http404
from django.shortcuts import render
from django.db.models import Max, Min, Sum
from .models import Board, Topic, Post
from datetime import datetime, timezone


def forum_view(request):
    title = 'Wieczorne narady'
    boards = Board.objects.all()
    posts = Post.objects.all()

    boards_with_posts_sum = {}
    for board in boards:
        posts_sum = 0
        for topic in board.topics.all():
            posts_sum += topic.posts.all().count()
        boards_with_posts_sum[board] = posts_sum

    boards_with_created_date = {}
    for board in boards:
        boards_with_created_date[board] = board.topics.all().aggregate(Min('created_date'))['created_date__min']

    boards_with_last_post_date = {}
    for board in boards:
        never = datetime(1970, 1, 1, tzinfo=timezone.utc)
        last_update_per_board = never
        for topic in board.topics.all():
            last_update_per_topic = (
                never if topic.posts.all().aggregate(Max('date_posted'))['date_posted__max'] is None
                else topic.posts.all().aggregate(Max('date_posted'))['date_posted__max']
            )
            if last_update_per_topic > last_update_per_board:
                last_update_per_board = last_update_per_topic
        boards_with_last_post_date[board] = (last_update_per_board if last_update_per_board != never else 0)

    boards_with_last_active_user = {}
    for board in boards:
        never = datetime(1970, 1, 1, tzinfo=timezone.utc)
        last_updated_date = never if boards_with_last_post_date[board] == 0 else boards_with_last_post_date[board]
        last_post = posts.filter(date_posted=last_updated_date)
        last_active_user = last_post[0].author if last_post else ''
        boards_with_last_active_user[board] = last_active_user

    context = {
        'title': title,
        'boards': boards,
        'boards_with_posts_sum': boards_with_posts_sum,
        'boards_with_created_date': boards_with_created_date,
        'boards_with_last_post_date': boards_with_last_post_date,
        'boards_with_last_active_user': boards_with_last_active_user
    }
    return render(request, 'forum/forum.html', context)


def board_topics_view(request, slug):
    try:
        board = Board.objects.get(slug=slug)
    except Board.DoesNotExist:
        raise Http404('Temat nie istnieje')

    title = board.title
    topics = board.topics.all()

    context = {
        'title': title,
        'board': board,
        'topics': topics,
    }
    return render(request, 'forum/board.html', context)


def topic_posts_view(request, topic_name):
    try:
        topic = Topic.objects.get(topic_name=topic_name)
    except Topic.DoesNotExist:
        raise Http404('Taka narada nie istnieje')

    title = topic.topic.name
    posts = topic.posts.all()

    context = {
        'title': title,
        'topic': topic,
        'posts': posts

    }
    return render(request, 'forum/topic.html', context)
