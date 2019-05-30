from django.http import Http404
from django.shortcuts import render
from django.db.models import Max, Min, Sum
from .models import Board, Topic, Post


def forum_view(request):
    title = 'Narady'
    boards = Board.objects.all()

    boards_with_posts_sum = {}
    for board in boards:
        posts_sum = 0
        for topic in board.topics.all():
            posts_sum += topic.posts.all().count()
        boards_with_posts_sum[board] = posts_sum

    boards_with_created_date = {}
    for board in boards:
        boards_with_created_date[board] = board.topics.all().aggregate(Min('created_date'))['created_date__min']

    boards_with_updated_date = {}
    for board in boards:
        boards_with_updated_date[board] = board.topics.all().aggregate(Max('created_date'))['created_date__max']

    # boards_with_last_active_user = {}
    # for board in boards:
    #     boards_with_last_active_user[board] =

    context = {
        'boards': boards,
        'title': title,
        'boards_with_posts_sum': boards_with_posts_sum,
        'boards_with_created_date': boards_with_created_date,
        'boards_with_updated_date': boards_with_updated_date
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
