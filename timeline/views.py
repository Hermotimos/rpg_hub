from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from users.models import Profile
from timeline.models import Event, EventNote, DescribedEvent, DescribedEventNote, GameSession
from timeline.forms import CreateEventForm, EventAddInformedForm, EditEventForm, EventNoteForm, DescribedEventNoteForm


@login_required
def timeline_view(request):

    if request.user.profile == Profile.objects.get(character_status='gm'):
        queryset = Event.objects.all()
    else:
        participated_qs = Profile.objects.get(user=request.user).events_participated.all()
        informed_qs = Profile.objects.get(user=request.user).events_informed.all()
        queryset = (participated_qs | informed_qs).distinct()

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
    obj = get_object_or_404(Event, id=event_id)

    if request.method == 'POST':
        form = EditEventForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, f'Zmodyfikowano wydarzenie!')
            return redirect('timeline')
    else:
        form = EditEventForm(instance=obj)

    context = {
        'page_title': 'Edycja wydarzenia',
        'form': form
    }
    return render(request, 'timeline/edit_event.html', context)


@login_required
def event_add_informed_view(request, event_id):
    obj = get_object_or_404(Event, id=event_id)

    participants = ', '.join(p.character_name.split(' ', 1)[0] for p in obj.participants.all())
    already_informed = obj.informed.all()[::1]                  # enforces evaluation of lazy Queryset for message
    informed = ', '.join(p.character_name.split(' ', 1)[0] for p in already_informed)

    if request.method == 'POST':
        form = EventAddInformedForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()

            if obj.season == 'spring':
                season = 'Wiosny'
            elif obj.season == 'summer':
                season = 'Lata'
            elif obj.season == 'autumn':
                season = 'Jesieni'
            else:
                season = 'Zimy'

            subject = f"[RPG] {request.user.profile} podzielił się z Tobą swoją historią!"
            message = f"{request.user.profile} znów rozprawia o swoich przygodach.\n" \
                      f"Oto kto już o nich słyszał: " \
                      f"{', '.join(p.character_name for p in form.cleaned_data['informed'])}\n\n" \
                      f"{obj.day_start}{'-' + obj.day_end if obj.day_end else ''}" \
                      f" dnia {season} {obj.year + 19}. " \
                      f"roku Archonatu Nemetha Samatiana rozegrało się co następuje:\n {obj.description}\n" \
                      f"A było to w miejscu: {obj.general_location}, " \
                      f"{[l.name for l in obj.specific_locations.all()]}.\n" \
                      f"Tak było i nie inaczej..."
            sender = settings.EMAIL_HOST_USER
            receivers_list = []

            currently_informed = form.cleaned_data['informed']
            for profile in currently_informed.all():
                if profile.user.email and profile in form.cleaned_data['informed'] and profile not in already_informed:
                    receivers_list.append(profile.user.email)
            send_mail(subject, message, sender, receivers_list)

            messages.success(request, f'Poinformowano wybrane postaci!')
            return redirect('timeline')
    else:
        form = EventAddInformedForm(instance=obj)

    context = {
        'page_title': 'Poinformuj o wydarzeniu',
        'form': form,
        'event': obj,
        'participants': participants,
        'informed': informed
    }
    return render(request, 'timeline/event_add_informed.html', context)


@login_required
def event_note_view(request, event_id):
    obj = get_object_or_404(Event, id=event_id)

    current_note = None
    participants = ', '.join(p.character_name.split(' ', 1)[0] for p in obj.participants.all())
    informed = ', '.join(p.character_name.split(' ', 1)[0] for p in obj.informed.all())

    try:
        current_note = EventNote.objects.get(event=obj, author=request.user)
    except EventNote.DoesNotExist:
        pass

    if request.method == 'POST':
        form = EventNoteForm(request.POST, instance=current_note)
        if form.is_valid():
            note = form.save(commit=False)
            note.author = request.user
            note.event = obj
            note.save()
            messages.success(request, f'Dodano notatkę!')
            return redirect('timeline')
    else:
        form = EventNoteForm(instance=current_note)

    context = {
        'page_title': 'Notatka',
        'event': obj,
        'form': form,
        'participants': participants,
        'informed': informed
    }
    return render(request, 'timeline/event_note.html', context)


@login_required
def described_event_note_view(request, event_id):
    obj = get_object_or_404(DescribedEvent, id=event_id)

    current_note = None
    participants = ', '.join(p.character_name.split(' ', 1)[0] for p in obj.participants.all())
    informed = ', '.join(p.character_name.split(' ', 1)[0] for p in obj.informed.all())

    try:
        current_note = DescribedEventNote.objects.get(event=obj, author=request.user)
    except DescribedEventNote.DoesNotExist:
        pass

    if request.method == 'POST':
        form = DescribedEventNoteForm(request.POST, instance=current_note)
        if form.is_valid():
            note = form.save(commit=False)
            note.author = request.user
            note.event = obj
            note.save()
            messages.success(request, f'Dodano notatkę!')
            _next = request.POST.get('next', '/')
            return HttpResponseRedirect(_next)                             # TODO
    else:
        form = DescribedEventNoteForm(instance=current_note)

    context = {
        'page_title': 'Notatka',
        'event': obj,
        'form': form,
        'participants': participants,
        'informed': informed
    }
    return render(request, 'timeline/described_event_note.html', context)


def is_allowed_game(_game, profile):
    for event in _game.described_events.all():
        if profile in event.participants.all() or profile in event.informed.all() or profile.character_status == 'gm':
            return True
    return False


@login_required
def chronicles_chapters_view(request):
    games = GameSession.objects.all()
    allowed_games_list = [g for g in games if is_allowed_game(g, request.user.profile)]

    context = {
        'page_title': 'Historia',
        'allowed_games_list': allowed_games_list
    }
    return render(request, 'timeline/chronicles_chapters.html', context)


@login_required
def chronicles_all_view(request):
    games = GameSession.objects.all()
    allowed_games_list = [g for g in games if is_allowed_game(g, request.user.profile)]

    context = {
        'page_title': 'Pełna historia',
        'allowed_games_list': allowed_games_list
    }
    return render(request, 'timeline/chronicles_all.html', context)


@login_required
def chronicles_one_chapter_view(request, game_no):
    obj = GameSession.objects.get(game_no=game_no)

    context = {
        'page_title': f'{obj.title.split(": ", 1)[0]}\n"{obj.title.split(": ", 1)[1]}"',

        'game': obj
    }
    return render(request, 'timeline/chronicles_one_chapter.html', context)
