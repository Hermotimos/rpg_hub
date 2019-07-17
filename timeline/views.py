from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from timeline.models import Event
from timeline.forms import CreateOrEditEvent


@login_required
def timeline_view(request):
    event_list = Event.objects.all()

    context = {
        'page_title': 'Kalendarium',
        'event_list': event_list
    }
    return render(request, 'timeline/timeline.html', context)


@login_required
def create_event_view(request):
    if request.method == 'POST':
        event_form = CreateOrEditEvent(request or None)
        if event_form.is_valid():
            event_form.save()
            return redirect('timeline')
    else:
        event_form = CreateOrEditEvent()

    context = {
        'page_title': 'Nowe wydarzenie',
        'event_form': event_form
    }
    return render(request, 'timeline/create-event.html', context)




# @login_required
# def edit_event_view(request, event_id):
#     event = get_object_or_404(Event, id=event_id)
#
#     context = {
#         'page_title': 'Edycja wydarzenia',
#         'event': event
#     }
#     return render(request, 'timeline/edit-event.html', context)

#
#
# @login_required
# def event_add_informed_view(request, event_id):
#     event = Event.objects.get(id=event_id)
#
#     context = {
#         'page_title': 'Kalendarium: poinformuj',
#         'event': event
#     }
#     return render(request, 'timeline/timeline.html', context)
