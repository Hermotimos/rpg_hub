from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from users.models import Profile


@login_required
def timeline_view(request):

    context = {
        'page_title': 'Kalendarium'
    }
    return render(request, 'timeline/timeline.html', context)
