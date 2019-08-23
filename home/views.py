from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required


@login_required
def home_view(request):
    return render(request, 'home/home.html')
