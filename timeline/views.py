from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from timeline.models import Event


@login_required
def timeline_view(request):
    event_list = Event.objects.all()

    context = {
        'page_title': 'Kalendarium',
        'event_list': event_list
    }
    return render(request, 'timeline/timeline.html', context)
