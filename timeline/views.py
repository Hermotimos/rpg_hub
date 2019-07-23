from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.mail import send_mail
from users.models import User, Profile
from timeline.models import Event, EventNote
from timeline.forms import CreateEventForm, EventAddInformedForm, EditEventForm, EventNoteForm


@login_required
def timeline_view(request):

    if request.user.profile == Profile.objects.get(character_status='gm'):
        queryset = Event.objects.all()
    else:
        participated_qs = Profile.objects.get(user=request.user).events_participated.all()
        informed_qs = Profile.objects.get(user=request.user).events_informed.all()
        queryset = participated_qs.union(informed_qs).iterator()

    seasons_with_styles_dict = {
        '1': 'season-spring',
        '2': 'season-summer',
        '3': 'season-autumn',
        '4': 'season-winter'
    }

    context = {
        'page_title': 'Kalendarium',
        'queryset': queryset,
        'seasons_with_styles_dict': seasons_with_styles_dict,
    }
    return render(request, 'timeline/timeline.html', context)


@login_required
def create_event_view(request):
    if request.method == 'POST':
        form = CreateEventForm(request.POST or None)
        if form.is_valid():
            event = form.save()
            event.threads.set(form.cleaned_data['threads'])
            event.participants.set(form.cleaned_data['participants'])
            event.informed.set(form.cleaned_data['informed'])
            event.specific_locations.set(form.cleaned_data['specific_locations'])
            event.save()
            messages.success(request, f'Dodano wydarzenie!')
            return redirect('timeline')
    else:
        form = CreateEventForm()

    context = {
        'page_title': 'Nowe wydarzenie',
        'form': form
    }
    return render(request, 'timeline/create_event.html', context)


@login_required
def edit_event_view(request, event_id):
    current_event = get_object_or_404(Event, id=event_id)

    if request.method == 'POST':
        form = EditEventForm(request.POST, instance=current_event)
        if form.is_valid():
            form.save()
            messages.success(request, f'Zmodyfikowano wydarzenie!')
            return redirect('timeline')
    else:
        form = EditEventForm(instance=current_event)

    context = {
        'page_title': 'Edycja wydarzenia',
        'form': form
    }
    return render(request, 'timeline/edit_event.html', context)


@login_required
def event_add_informed_view(request, event_id):
    current_event = get_object_or_404(Event, id=event_id)

    if request.method == 'POST':
        form = EventAddInformedForm(request.POST, instance=current_event)
        if form.is_valid():
            form.save()

            if current_event.season == 'spring':
                season = 'Wiosny'
            elif current_event.season == 'summer':
                season = 'Lata'
            elif current_event.season == 'autumn':
                season = 'Jesieni'
            else:
                season = 'Zimy'

            subject = f"[RPG] {request.user.profile} opowiedział o swoich przygodach"
            message = f"{request.user.profile} znów rozprawia o swoich przygodach.\n" \
                      f"Oto kto już o nich słyszał: " \
                      f"{[p.character_name for p in form.cleaned_data['informed']]}\n\n" \
                      f"{current_event.day_start}{'-' + current_event.day_end if current_event.day_end else ''}" \
                      f" dnia {season} {current_event.year + 19}. " \
                      f"roku Archonatu Nemetha Samatiana rozegrało się co następuje:\n {current_event.description}\n" \
                      f"A było to w miejscu: {current_event.general_location}, " \
                      f"{[l.name for l in current_event.specific_locations.all()]}.\n" \
                      f"Tak było i nie inaczej..."
            sender = settings.EMAIL_HOST_USER
            receivers_list = []
            for user in User.objects.all():
                if user.profile in form.cleaned_data['informed']:
                    receivers_list.append(user.email)
            send_mail(subject, message, sender, receivers_list)

            messages.success(request, f'Poinformowano wybrane postaci!')
            return redirect('timeline')
    else:
        form = EventAddInformedForm(instance=current_event)

    context = {
        'page_title': 'Poinformuj o wydarzeniu',
        'form': form,
        'current_event': current_event
    }
    return render(request, 'timeline/event_add_informed.html', context)


@login_required
def event_note_view(request, event_id):
    current_event = get_object_or_404(Event, id=event_id)
    current_note = None

    try:
        current_note = EventNote.objects.get(event=current_event, author=request.user)
    except EventNote.DoesNotExist:
        pass

    if request.method == 'POST':
        form = EventNoteForm(request.POST, instance=current_note)
        if form.is_valid():
            note = form.save(commit=False)
            note.author = request.user
            note.event = current_event
            note.save()
            messages.success(request, f'Dodano notatkę!')
            return redirect('timeline')
    else:
        form = EventNoteForm(instance=current_note)

    context = {
        'page_title': 'Notatka',
        'current_event': current_event,
        'form': form
    }
    return render(request, 'timeline/event_note.html', context)
