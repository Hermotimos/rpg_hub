from django.shortcuts import render
from .models import Board


# Create your views here.
def forum_view(request):
    boards = Board.objects.all()
    return render(request, 'forum.html', {'boards': boards})
