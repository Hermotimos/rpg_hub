from django.shortcuts import render
from .models import Board, Topic, Post


def forum_view(request):
    title = 'Narady'
    boards = Board.objects.all()

    context = {
        'boards': boards,
        'title': title
    }
    return render(request, 'forum.html', context)


def board_topics_view(request, slug):
    board = Board.objects.get(slug=slug)
    title = board.title

    topics = board.topics.all()
    context = {
        'title': title,
        'board': board,
        'topics': topics,
    }
    return render(request, 'board.html', context)
