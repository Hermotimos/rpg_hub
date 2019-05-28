from django.shortcuts import render
from .models import Board, Topic, Post


def forum_view(request):
    boards = Board.objects.all()
    title = 'Narady'
    context = {
        'boards': boards,
        'title': title
    }
    return render(request, 'forum.html', context)


def board_view(request, board_id):
    board = Board.objects.get(id=board_id)
    topics = Topic.objects.all()
    context = {
        'board': board,
        'topics': topics,
    }
    return render(request, 'board.html', context)
