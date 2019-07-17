from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from timeline.models import Event, GeneralLocation, SpecificLocation, GameSession
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
        event_form = CreateOrEditEvent(request.POST or None)
        if event_form.is_valid():
            event = event_form.save(commit=False)
            # event.general_location = GeneralLocation.objects.get(name=event_form.cleaned_data['general_location'])
            # event.game_no = GameSession.objects.get()
            event.save()

            threads_cleaned = event_form.cleaned_data['threads']
            event.threads.set(threads_cleaned)

            participants_cleaned = event_form.cleaned_data['participants']
            event.participants.set(participants_cleaned)

            informed_cleaned = event_form.cleaned_data['informed']
            event.informed.set(informed_cleaned)

            specific_locations_cleaned = event_form.cleaned_data['specific_locations']
            event.specific_locations.set(specific_locations_cleaned)

            event.save()
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
