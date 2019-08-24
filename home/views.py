from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def home_view(request):
    return render(request, 'home/home.html')


@login_required
def dupa_view(request):
    return render(request, 'home/dupa.html', {'page_title': 'Dupa'})
