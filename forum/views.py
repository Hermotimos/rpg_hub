from django.http import Http404
from django.shortcuts import render
from .models import Board, Topic, Post


def forum_view(request):
    title = 'Narady'
    boards = Board.objects.all()

    boards_with_posts_sum = {}
    for board in boards:
        posts_sum = 0
        for topic in board.topics.all():
            posts_sum += topic.posts.all().count()
        boards_with_posts_sum[board.title] = posts_sum

    context = {
        'boards': boards,
        'title': title,
        'boards_with_posts_sum': boards_with_posts_sum,
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
