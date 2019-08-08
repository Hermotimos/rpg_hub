from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required


@login_required
def home_view(request):
    return redirect('users:login')
