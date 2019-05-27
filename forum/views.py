from django.shortcuts import render
from .models import Board


def forum_view(request):
    boards = Board.objects.all()
    title = 'Narady'
    context = {
        'boards': boards,
        'title': title
    }
    return render(request, 'forum.html', context)
