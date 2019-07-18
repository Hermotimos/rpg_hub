from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.mail import send_mail
from users.models import User
from timeline.models import Event, EventNote
from timeline.forms import CreateEventForm, EventAddInformedForm, EditEventForm, EventNoteForm, ReportForm


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
        event_form = CreateEventForm(request.POST or None)
        if event_form.is_valid():
            event = event_form.save()
            event.threads.set(event_form.cleaned_data['threads'])
            event.participants.set(event_form.cleaned_data['participants'])
            event.informed.set(event_form.cleaned_data['informed'])
            event.specific_locations.set(event_form.cleaned_data['specific_locations'])
            event.save()
            messages.success(request, f'Dodano wydarzenie!')
            return redirect('timeline')
    else:
        event_form = CreateEventForm()

    context = {
        'page_title': 'Nowe wydarzenie',
        'event_form': event_form
    }
    return render(request, 'timeline/create_event.html', context)


@login_required
def edit_event_view(request, event_id):
    current_event = get_object_or_404(Event, id=event_id)

    if request.method == 'POST':
        edit_event_form = EditEventForm(request.POST, instance=current_event)
        if edit_event_form.is_valid():
            edit_event_form.save()
            messages.success(request, f'Zmodyfikowano wydarzenie!')
            return redirect('timeline')
    else:
        edit_event_form = EditEventForm(instance=current_event)

    context = {
        'page_title': 'Edycja wydarzenia',
        'edit_event_form': edit_event_form
    }
    return render(request, 'timeline/edit_event.html', context)


@login_required
def event_add_informed_view(request, event_id):
    current_event = get_object_or_404(Event, id=event_id)

    if request.method == 'POST':
        add_informed_form = EventAddInformedForm(request.POST, instance=current_event)
        if add_informed_form.is_valid():
            add_informed_form.save()

            subject = f"[RPG] {request.user.profile} opowiedział Ci o swoich przygodach"
            message = f"{request.user.profile} dołączył uczestnika/-ów do narady.\n"
            sender = settings.EMAIL_HOST_USER
            receivers_list = []
            for user in User.objects.all():
                if user.profile in add_informed_form.cleaned_data['informed']:
                    receivers_list.append(user.email)
            send_mail(subject, message, sender, receivers_list)

            messages.success(request, f'Poinformowano wybrane postaci!')
            return redirect('timeline')
    else:
        add_informed_form = EventAddInformedForm(instance=current_event)

    context = {
        'page_title': 'Poinformuj o wydarzeniu',
        'add_informed_form': add_informed_form,
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
        note_form = EventNoteForm(request.POST, instance=current_note)
        if note_form.is_valid():
            note = note_form.save(commit=False)
            note.author = request.user
            note.event = current_event
            note.save()
            messages.success(request, f'Dodano notatkę!')
            return redirect('timeline')
    else:
        note_form = EventNoteForm(instance=current_note)

    context = {
        'page_title': 'Notatka',
        'current_event': current_event,
        'note_form': note_form
    }
    return render(request, 'timeline/event_note.html', context)


@login_required
def report_view(request, event_id):
    current_event = get_object_or_404(Event, id=event_id)

    if request.method == 'POST':
        report_form = ReportForm(request.POST or None)
        if report_form.is_valid():

            subject = f"[RPG] Problem"
            message = f"{request.user.profile} zgłosił problem:\n" \
                      f"Wydarzenie: {current_event.description}\n" \
                      f"Zgłoszenie: {report_form.cleaned_data['text']}\n" \
                      f"Link do edycji wydarzenia: {request.get_host()}/timeline/{current_event.id}/edit-event/"
            sender = settings.EMAIL_HOST_USER
            receivers_list = ['lukas.kozicki@gmail.com']
            send_mail(subject, message, sender, receivers_list)

            messages.success(request, f'MG został poinformowany o problemie!')
            return redirect('timeline')
    else:
        report_form = ReportForm()

    context = {
        'page_title': 'Zgłoś problem',
        'report_form': report_form,
        'current_event': current_event
    }
    return render(request, 'timeline/report.html', context)
