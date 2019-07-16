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


@login_required
def event_add_informed_view(request, event_id):
    event = Event.objects.get(id=event_id)

    context = {
        'page_title': 'Kalendarium: poinformuj',
        'event': event
    }
    return render(request, 'timeline/timeline.html', context)
