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


# @login_required
# def thread_view(request, thread_name):
#
#
#     context = {}
#     return render(request, 'timeline/thread.html', context)


@login_required
def timeline__filtered_view(request, year=None, thread_id=None, general_location=None, specific_location=None):
    event_list = Event.objects.all()

    if year is not None:
        event_list = event_list.objects.filter(year=year)
        if thread_id is not None:
            event_list = event_list.objects.filter(thread=thread_id)
            if general_location is not None:
                event_list = event_list.objects.filter(general_location=general_location)
                if specific_location is not None:
                    event_list = event_list.objects.filter(specific_location=specific_location)


    context = {
        'page_title': 'Kalendarium [filtered]',
        'event_list': event_list
    }
    return render(request, 'timeline/timeline-filtered.html', context)
