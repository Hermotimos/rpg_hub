from django.http import Http404
from django.shortcuts import render
from django.db.models import Max
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

    boards_with_last_updated = {}
    for board in boards:
        boards_with_last_updated[board] = board.topics.all().aggregate(Max('last_updated'))['last_updated__max']

    context = {
        'boards': boards,
        'title': title,
        'boards_with_posts_sum': boards_with_posts_sum,
        'boards_with_last_updated': boards_with_last_updated
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
