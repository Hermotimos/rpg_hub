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
def timeline__filtered_view(request, year=None, thread=None, participants_choice=None, location1=None, location2=None):
    event_list = Event.objects.all()
    criteria = year, thread, participants_choice, location1, location2
    for criterion in criteria:
        if criterion is not None:
            event_list = Event.objects.get(criterion=criterion)

    context = {
        'page_title': 'Kalendarium',
        'event_list': event_list
    }
    return render(request, 'timeline/timeline.html', context)
