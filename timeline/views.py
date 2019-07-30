import locale
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from users.models import Profile
from timeline.models import Event, EventNote, DescribedEvent, DescribedEventNote, GameSession, Thread, GeneralLocation,\
    SpecificLocation
from timeline.forms import CreateEventForm, EventAddInformedForm, EditEventForm, EventNoteForm, DescribedEventNoteForm,\
    CreateDescribedEventForm, DescribedEventAddInformedForm, EditDescribedEventForm


# #################### TIMELINE: model Event ####################

SEASONS_WITH_STYLES_DICT = {
    '1': 'season-spring',
    '2': 'season-summer',
    '3': 'season-autumn',
    '4': 'season-winter'
}


@login_required
def timeline_main_view(request):
    if request.user.profile in Profile.objects.filter(character_status='gm'):
        queryset = Event.objects.all()
    else:
        participated_qs = Profile.objects.get(user=request.user).events_participated.all()
        informed_qs = Profile.objects.get(user=request.user).events_informed.all()
        queryset = (participated_qs | informed_qs).distinct()

    # years
    years_set = {e.year for e in queryset.all()}
    years_sorted_list = list(years_set)
    years_sorted_list.sort()

    # threads
    threads_set = set()
    threads_querysets_list = [event.threads.all() for event in queryset]
    for qs in threads_querysets_list:
        for th in qs:
            threads_set.add(th)
    threads_name_and_obj_list = [(t.name, t) for t in threads_set]
    threads_name_and_obj_list.sort()

    # participants
    participants_set = set()
    participants_querysets_list = [event.participants.all() for event in queryset]
    for qs in participants_querysets_list:
        for p in qs:
            participants_set.add(p)
    participants_name_and_obj_list = [(t.character_name, t) for t in participants_set]
    participants_name_and_obj_list.sort()

    # specific locations
    specific_locations_set = set()
    specific_locations_querysets_list = [event.specific_locations.all() for event in queryset]
    for qs in specific_locations_querysets_list:
        for sl in qs:
            specific_locations_set.add(sl)
    specific_locations_name_and_obj_list = [(t.name, t) for t in specific_locations_set]
    specific_locations_name_and_obj_list.sort()

    # general locations with their specific locations
    general_locations_set = {event.general_location for event in queryset}
    general_locs_with_specific_locs_list = []
    for gl in general_locations_set:
        general_loc_with_specific_locs_list = [gl, [sl for sl in specific_locations_name_and_obj_list if sl[1].general_location == gl]]
        general_locs_with_specific_locs_list.append(general_loc_with_specific_locs_list)

    context = {
        'page_title': 'Kalendarium',
        'seasons_with_styles_dict': SEASONS_WITH_STYLES_DICT,
        'years': years_sorted_list,
        'threads': threads_name_and_obj_list,
        'participants': participants_name_and_obj_list,
        'general_locs_with_specific_locs_list': general_locs_with_specific_locs_list,
        'queryset': queryset
    }
    return render(request, 'timeline/timeline_main.html', context)


@login_required
def timeline_events_view(request):
    if request.user.profile in Profile.objects.filter(character_status='gm'):
        queryset = Event.objects.all()
    else:
        participated_qs = Profile.objects.get(user=request.user).events_participated.all()
        informed_qs = Profile.objects.get(user=request.user).events_informed.all()
        queryset = (participated_qs | informed_qs).distinct()

    context = {
        'page_title': 'Pełne Kalendarium',
        'queryset': queryset,
        'seasons_with_styles_dict': SEASONS_WITH_STYLES_DICT,
    }
    return render(request, 'timeline/timeline_events.html', context)


@login_required
def timeline_by_thread_view(request, thread_id):
    thread = Thread.objects.get(id=thread_id)
    events_by_thread_qs = thread.events.all()

    if request.user.profile in Profile.objects.filter(character_status='gm'):
        queryset = events_by_thread_qs
    else:
        participated_qs = Profile.objects.get(user=request.user).events_participated.all()
        informed_qs = Profile.objects.get(user=request.user).events_informed.all()
        events_by_user = (participated_qs | informed_qs).distinct()
        queryset = [e for e in events_by_user if e in events_by_thread_qs]

    context = {
        'page_title': f'Kalendarium: {thread.name}',
        'queryset': queryset,
        'seasons_with_styles_dict': SEASONS_WITH_STYLES_DICT,

    }
    return render(request, 'timeline/timeline_events.html', context)

#
# @login_required
# def timeline_by_participant_view(request, participant_id):
#
#     context = {
#         'page_title': 'XXXXXXXXXXX',
#     }
#     return render(request, 'timeline/XXXXX.html', context)
#
#
# @login_required
# def timeline_by_location_general_view(request, location_general_id):
#
#     context = {
#         'page_title': 'XXXXXXXXXXX',
#     }
#     return render(request, 'timeline/XXXXX.html', context)
#
#
# @login_required
# def timeline_by_location_specific_view(request, location_specific_id):
#
#     context = {
#         'page_title': 'XXXXXXXXXXX',
#     }
#     return render(request, 'timeline/XXXXX.html', context)
#
#
# @login_required
# def timeline_by_year_view(request, year):
#
#     context = {
#         'page_title': 'XXXXXXXXXXX',
#     }
#     return render(request, 'timeline/XXXXX.html', context)
#

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
            return redirect('timeline-main')
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
            return redirect('timeline-main')
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
            return redirect('timeline-main')
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
            return redirect('timeline-main')
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


# #################### CHRONICLES: model DescribedEvent ####################


@login_required
def create_described_event_view(request):
    if request.method == 'POST':
        form = CreateDescribedEventForm(request.POST or None)
        if form.is_valid():
            event = form.save()
            event.participants.set(form.cleaned_data['participants'])
            event.informed.set(form.cleaned_data['informed'])
            event.save()
            messages.success(request, f'Dodano wydarzenie!')
            return redirect('chronicles_all')
    else:
        form = CreateDescribedEventForm()

    context = {
        'page_title': 'Nowe wydarzenie',
        'form': form
    }
    return render(request, 'chronicles/create_described_event.html', context)


@login_required
def edit_described_event_view(request, event_id):
    obj = get_object_or_404(DescribedEvent, id=event_id)

    if request.method == 'POST':
        form = EditDescribedEventForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, f'Zmodyfikowano wydarzenie!')
            _next = request.POST.get('next', '/')
            return HttpResponseRedirect(_next)
    else:
        form = EditDescribedEventForm(instance=obj)

    context = {
        'page_title': 'Edycja wydarzenia',
        'form': form
    }
    return render(request, 'chronicles/edit_described_event.html', context)


@login_required
def described_event_add_informed_view(request, event_id):
    obj = get_object_or_404(DescribedEvent, id=event_id)

    participants = ', '.join(p.character_name.split(' ', 1)[0] for p in obj.participants.all())
    already_informed = obj.informed.all()[::1]                  # enforces evaluation of lazy Queryset for message
    informed = ', '.join(p.character_name.split(' ', 1)[0] for p in already_informed)

    if request.method == 'POST':
        form = DescribedEventAddInformedForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()

            subject = f"[RPG] {request.user.profile} podzielił się z Tobą swoją historią!"
            message = f"{request.user.profile} znów rozprawia o swoich przygodach.\n" \
                      f"Oto kto już o nich słyszał: " \
                      f"{', '.join(p.character_name for p in form.cleaned_data['informed'])}\n\n" \
                      f"Podczas przygody '{obj.game_no.title}' rozegrało się co następuje:\n {obj.description}\n" \
                      f"Tak było i nie inaczej..."
            sender = settings.EMAIL_HOST_USER
            receivers_list = []

            currently_informed = form.cleaned_data['informed']
            for profile in currently_informed.all():
                if profile.user.email and profile in form.cleaned_data['informed'] and profile not in already_informed:
                    receivers_list.append(profile.user.email)
            send_mail(subject, message, sender, receivers_list)

            messages.success(request, f'Poinformowano wybrane postaci!')
            _next = request.POST.get('next', '/')
            return HttpResponseRedirect(_next)
    else:
        form = DescribedEventAddInformedForm(instance=obj)

    context = {
        'page_title': 'Poinformuj o wydarzeniu',
        'form': form,
        'event': obj,
        'participants': participants,
        'informed': informed
    }
    return render(request, 'chronicles/described_event_add_informed.html', context)


def is_allowed_game(_game, profile):
    for event in _game.described_events.all():
        if profile in event.participants.all() or profile in event.informed.all() or profile.character_status == 'gm':
            return True
    return False


@login_required
def chronicles_chapters_view(request):
    games = GameSession.objects.all()
    allowed_bios_list = [g for g in games if is_allowed_game(g, request.user.profile) and g.game_no < 0]
    allowed_games_list = [g for g in games if is_allowed_game(g, request.user.profile) and g.game_no > 0]

    context = {
        'page_title': 'Historia',
        'allowed_bios_list': allowed_bios_list,
        'allowed_games_list': allowed_games_list
    }
    return render(request, 'chronicles/chronicles_chapters.html', context)


@login_required
def chronicles_all_view(request):
    games = GameSession.objects.all()
    allowed_bios_list = [g for g in games if is_allowed_game(g, request.user.profile) and g.game_no < 0]
    allowed_games_list = [g for g in games if is_allowed_game(g, request.user.profile) and g.game_no > 0]

    context = {
        'page_title': 'Pełna historia drużyny',
        'allowed_bios_list': allowed_bios_list,
        'allowed_games_list': allowed_games_list
    }
    return render(request, 'chronicles/chronicles_all.html', context)


@login_required
def chronicles_one_chapter_view(request, game_id):
    obj = get_object_or_404(GameSession, id=game_id)

    if ':' in obj.title:
        page_title = f'{obj.title.split(": ", 1)[0]}:\n"{obj.title.split(": ", 1)[1]}"'
    else:
        page_title = obj.title

    context = {
        'page_title': page_title,
        'game': obj
    }
    return render(request, 'chronicles/chronicles_one_chapter.html', context)


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
            return HttpResponseRedirect(_next)
    else:
        form = DescribedEventNoteForm(instance=current_note)

    context = {
        'page_title': 'Notatka',
        'event': obj,
        'form': form,
        'participants': participants,
        'informed': informed
    }
    return render(request, 'chronicles/described_event_note.html', context)