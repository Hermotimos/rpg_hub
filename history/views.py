from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from users.models import Profile
from history.models import (TimelineEvent,
                            TimelineEventNote,
                            ChronicleEvent,
                            ChronicleEventNote,
                            Chapter,
                            GameSession,
                            Thread,
                            GeneralLocation,
                            SpecificLocation)
from history.forms import (TimelineEventCreateForm,
                           TimelineEventInformForm,
                           TimelineEventEditForm,
                           TimelineEventNoteForm,
                           ChronicleEventNoteForm,
                           ChronicleEventCreateForm,
                           ChronicleEventInformForm,
                           ChronicleEventEditForm)


# #################### CHRONICLE: model ChronicleEvent ####################


def is_allowed_for_chronicle(profile, chapter_id=0, game_id=0, chronicle_event_id=0, timeline_event_id=0):
    if profile.character_status == 'gm':
        return True
    elif chapter_id:
        for game in Chapter.objects.get(id=chapter_id).game_sessions.all():
            for event in game.chronicle_events.all():
                if profile in event.participants.all() or profile in event.informed.all():
                    return True
    elif game_id:
        for event in GameSession.objects.get(id=game_id).chronicle_events.all():
            if profile in event.participants.all() or profile in event.informed.all():
                return True
    elif chronicle_event_id:
        if profile in ChronicleEvent.objects.get(id=chronicle_event_id).participants.all() \
                or profile in ChronicleEvent.objects.get(id=chronicle_event_id).informed.all():
            return True
    elif timeline_event_id:
        if profile in TimelineEvent.objects.get(id=timeline_event_id).participants.all() \
                or profile in ChronicleEvent.objects.get(id=timeline_event_id).informed.all():
            return True
    else:
        return False


@login_required
def chronicle_main_view(request):
    if request.user.profile.character_status == 'gm':
        chapters_with_games_dict = {ch: [g for g in ch.game_sessions.all()] for ch in Chapter.objects.all()}
    else:
        events_participated = request.user.profile.chronicle_events_participated.all()
        events_informed = request.user.profile.chronicle_events_informed.all()
        events = (events_participated | events_informed).distinct()
        events = list(events)
        games = [e.game for e in events]
        chapters = [g.chapter for g in games]
        chapters_with_games_dict = {ch: [g for g in ch.game_sessions.all() if g in games] for ch in chapters}

    context = {
        'page_title': 'Kronika',
        'chapters_with_games_dict': chapters_with_games_dict
    }
    return render(request, 'history/chronicle_main.html', context)


@login_required
def chronicle_create_view(request):
    if request.method == 'POST':
        form = ChronicleEventCreateForm(request.POST)
        if form.is_valid():
            event = form.save()
            event.participants.set(form.cleaned_data['participants'])
            event.informed.set(form.cleaned_data['informed'])
            event.save()
            messages.info(request, f'Dodano nowe wydarzenie!')
            _next = request.POST.get('next', '/')
            return HttpResponseRedirect(_next)
        else:
            messages.warning(request, 'Popraw poniższy błąd!')
    else:
        form = ChronicleEventCreateForm()

    context = {
        'page_title': 'Nowe wydarzenie: Kronika',
        'form': form
    }
    return render(request, 'history/chronicle_create.html', context)


@login_required
def chronicle_all_chapters_view(request):
    if request.user.profile.character_status == 'gm':
        events_informed = []
        chapters_with_games_dict = {ch: [g for g in ch.game_sessions.all()] for ch in Chapter.objects.all()}
        games_with_events_dict = {g: [e for e in g.chronicle_events.all()] for g in GameSession.objects.all()}
    else:
        events_participated = request.user.profile.chronicle_events_participated.all()
        events_informed = request.user.profile.chronicle_events_informed.all()
        events = (events_participated | events_informed).distinct()

        events_informed = list(events_informed)
        events = list(events)
        games = [e.game for e in events]
        chapters = [g.chapter for g in games]
        chapters_with_games_dict = {ch: [g for g in ch.game_sessions.all() if g in games] for ch in chapters}
        games_with_events_dict = {g: [e for e in g.chronicle_events.all() if e in events] for g in games}

    context = {
        'page_title': 'Pełna kronika',
        'chapters_with_games_dict': chapters_with_games_dict,
        'games_with_events_dict': games_with_events_dict,
        'events_informed': events_informed
    }
    return render(request, 'history/chronicle_all_chapters.html', context)


@login_required
def chronicle_one_chapter_view(request, chapter_id):
    chapter = get_object_or_404(Chapter, id=chapter_id)
    if request.user.profile.character_status == 'gm':
        games_with_events_dict = {g: [e for e in g.chronicle_events.all()] for g in chapter.game_sessions.all()}
        events_informed = []
    else:
        events_participated = request.user.profile.chronicle_events_participated.filter(game__in=chapter.game_sessions.all())
        events_informed = request.user.profile.chronicle_events_informed.filter(game__in=chapter.game_sessions.all())
        events = (events_participated | events_informed).distinct()
        events_informed = list(events_informed)
        events = list(events)

        games = [e.game for e in events]
        games_with_events_dict = {g: [e for e in g.chronicle_events.all() if e in events] for g in games}

    context = {
        'page_title': f'{chapter.title}',
        'games_with_events_dict': games_with_events_dict,
        'events_informed': events_informed
    }
    if is_allowed_for_chronicle(request.user.profile, chapter_id=chapter_id):
        return render(request, 'history/chronicle_one_chapter.html', context)
    else:
        return redirect('home:dupa')


@login_required
def chronicle_one_game_view(request, game_id):
    game = get_object_or_404(GameSession, id=game_id)
    if request.user.profile.character_status == 'gm':
        events_informed = []
        events = game.chronicle_events.all()
        events = list(events)
    else:
        events_participated = request.user.profile.chronicle_events_participated.filter(game=game)
        events_informed = request.user.profile.chronicle_events_informed.filter(game=game)
        events = (events_participated | events_informed).distinct()
        events_informed = list(events_informed)
        events = list(events)

    context = {
        'page_title': f'{game.title}',
        'events': events,
        'events_informed': events_informed
    }
    if is_allowed_for_chronicle(request.user.profile, game_id=game_id):
        return render(request, 'history/chronicle_one_game.html', context)
    else:
        return redirect('home:dupa')


@login_required
def chronicle_inform_view(request, event_id):
    event = get_object_or_404(ChronicleEvent, id=event_id)

    participants_str = ', '.join(p.character_name.split(' ', 1)[0] for p in event.participants.all())
    participants_ids = [p.id for p in event.participants.all()]
    old_informed = event.informed.all()[::1]                  # enforces evaluation of lazy Queryset for message
    old_informed_ids = [p.id for p in old_informed]
    old_informed_str = ', '.join(p.character_name.split(' ', 1)[0] for p in old_informed)

    if request.method == 'POST':
        form = ChronicleEventInformForm(authenticated_user=request.user,
                                        old_informed_ids=old_informed_ids,
                                        participants_ids=participants_ids,
                                        data=request.POST,
                                        instance=event)
        if form.is_valid():
            event = form.save()

            informed = form.cleaned_data['informed']
            informed |= Profile.objects.filter(id__in=old_informed_ids)
            event.informed.set(informed)

            subject = f"[RPG] {request.user.profile} podzielił się z Tobą swoją historią!"
            message = f"{request.user.profile} znów rozprawia o swoich przygodach.\n" \
                      f"{', '.join(p.character_name for p in form.cleaned_data['informed'])}\n\n" \
                      f"Podczas przygody '{event.game.title}' rozegrało się co następuje:\n {event.description}\n" \
                      f"Tak było i nie inaczej...\n\n" \
                      f"Wydarzenie zostało zapisane w Twojej Kronice."
            sender = settings.EMAIL_HOST_USER
            receivers = []
            for profile in event.informed.all():
                # exclude previously informed users from mailing to avoid spam
                if profile not in old_informed:
                    receivers.append(profile.user.email)
            if request.user.profile.character_status != 'gm':
                receivers.append('lukas.kozicki@gmail.com')
            send_mail(subject, message, sender, receivers)

            messages.info(request, f'Poinformowałeś wybrane postaci!')
            _next = request.POST.get('next', '/')
            return HttpResponseRedirect(_next)
    else:
        form = ChronicleEventInformForm(authenticated_user=request.user,
                                        old_informed_ids=old_informed_ids,
                                        participants_ids=participants_ids)

    context = {
        'page_title': 'Poinformuj o wydarzeniu',
        'form': form,
        'event': event,
        'participants': participants_str,
        'informed': old_informed_str
    }
    if is_allowed_for_chronicle(request.user.profile, chronicle_event_id=event_id):
        return render(request, 'history/chronicle_inform.html', context)
    else:
        return redirect('home:dupa')


@login_required
def chronicle_note_view(request, event_id):
    event = get_object_or_404(ChronicleEvent, id=event_id)

    current_note = None
    participants = ', '.join(p.character_name.split(' ', 1)[0] for p in event.participants.all())
    informed = ', '.join(p.character_name.split(' ', 1)[0] for p in event.informed.all())

    try:
        current_note = ChronicleEventNote.objects.get(event=event, author=request.user)
    except ChronicleEventNote.DoesNotExist:
        pass

    if request.method == 'POST':
        form = ChronicleEventNoteForm(request.POST, instance=current_note)
        if form.is_valid():
            note = form.save(commit=False)
            note.author = request.user
            note.event = event
            note.save()
            messages.info(request, f'Dodano/zmieniono notatkę!')
            _next = request.POST.get('next', '/')
            return HttpResponseRedirect(_next)
    else:
        form = ChronicleEventNoteForm(instance=current_note)

    context = {
        'page_title': 'Przemyślenia',
        'event': event,
        'form': form,
        'participants': participants,
        'informed': informed
    }
    if is_allowed_for_chronicle(request.user.profile, chronicle_event_id=event_id):
        return render(request, 'history/chronicle_note.html', context)
    else:
        return redirect('home:dupa')


@login_required
def chronicle_edit_view(request, event_id):
    event = get_object_or_404(ChronicleEvent, id=event_id)

    if request.method == 'POST':
        form = ChronicleEventEditForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.info(request, f'Zmodyfikowano wydarzenie!')
            _next = request.POST.get('next', '/')
            return HttpResponseRedirect(_next)
    else:
        form = ChronicleEventEditForm(instance=event)

    context = {
        'page_title': 'Edycja wydarzenia',
        'form': form
    }
    if request.user.profile.character_status == 'gm':
        return render(request, 'history/chronicle_edit.html', context)
    else:
        return redirect('home:dupa')


# #################### TIMELINE: model TimelineEvent ####################


SEASONS_WITH_STYLES_DICT = {
    '1': 'season-spring',
    '2': 'season-summer',
    '3': 'season-autumn',
    '4': 'season-winter'
}


def participated_and_informed_events(profile_id):
    profile = Profile.objects.get(id=profile_id)
    if profile.character_status == 'gm':
        known_qs = TimelineEvent.objects.all()
    else:
        participated_qs = Profile.objects.get(id=profile_id).timeline_events_participated.all()
        informed_qs = Profile.objects.get(id=profile_id).timeline_events_informed.all()
        known_qs = (participated_qs | informed_qs).distinct()
    return known_qs


@login_required
def timeline_main_view(request):
    # for populating fields sorting_name on models Thread, Participant, Specific Location
    # for o in Thread.objects.all():
    #     o.save()
    # for o in GeneralLocation.objects.all():
    #     o.save()
    # for o in SpecificLocation.objects.all():
    #     o.save()

    known_events = participated_and_informed_events(request.user.profile.id)
    known_events = list(known_events)

    # repetitive interations over known_events.all():
    threads_querysets_list = []
    participants_querysets_list = []
    spec_locs_querysets_list = []
    gen_locs_set = set()
    games_set = set()
    years_set = set()
    for event in known_events:
        years_set.add(event.year)
        threads_querysets_list.append(event.threads.all())
        participants_querysets_list.append(event.participants.all())
        spec_locs_querysets_list.append(event.specific_locations.all())
        gen_locs_set.add(event.general_location)
        games_set.add(event.game)

    # threads
    threads_qs = Thread.objects.none()
    for qs in threads_querysets_list:
        threads_qs = threads_qs | qs
    threads_list = list(threads_qs.distinct())
    threads_name_and_obj_list = [(t.name, t) for t in threads_list]

    # participants
    # participants_set = set()
    # for qs in participants_querysets_list:
    #     for p in qs:
    #         participants_set.add(p)
    # participants_name_and_obj_list = [(t.character_name, t) for t in participants_set]
    # participants_name_and_obj_list.sort()

    participants_qs = Profile.objects.none()
    for qs in participants_querysets_list:
        participants_qs = participants_qs | qs
    participants_list = list(participants_qs.distinct())
    participants_name_and_obj_list = [(t.character_name, t) for t in participants_list]

    # specific locations
    # spec_locs_set = set()
    # for qs in spec_locs_querysets_list:
    #     for sl in qs:
    #         spec_locs_set.add(sl)
    # spec_locs_name_and_obj_list = [(t.name, t) for t in spec_locs_set]
    # spec_locs_name_and_obj_list.sort()

    spec_locs_qs = SpecificLocation.objects.none()
    for qs in spec_locs_querysets_list:
        spec_locs_qs = spec_locs_qs | qs
    spec_locs_list = list(spec_locs_qs.distinct())
    spec_locs_name_and_obj_list = [(t.name, t) for t in spec_locs_list]

    # general locations with their specific locations: LEFT UNSORTED TO REFLECT SUBSEQUENT GENERAL LOCATIONS IN GAME
    gen_locs_with_spec_locs_list = []
    for gl in gen_locs_set:
        gen_loc_with_spec_locs_list = [gl, [sl for sl in spec_locs_name_and_obj_list if sl[1].general_location == gl]]
        gen_locs_with_spec_locs_list.append(gen_loc_with_spec_locs_list)

    # games
    games_sorted_list = list(games_set)
    games_sorted_list.sort(key=lambda game: game.game_no)
    games_name_and_obj_list = [(g.title, g) for g in games_sorted_list]

    # years with their seasons
    years_sorted_list = list(years_set)
    years_sorted_list.sort()
    years_with_seasons_dict = {}
    for y in years_sorted_list:
        seasons_set = {e.season for e in known_events if e.year == y}
        seasons_sorted_list = list(seasons_set)
        seasons_sorted_list.sort()
        years_with_seasons_dict[y] = seasons_sorted_list

    context = {
        'page_title': 'Kalendarium',
        'seasons_with_styles_dict': SEASONS_WITH_STYLES_DICT,
        'years_with_seasons_dict': years_with_seasons_dict,
        'threads': threads_name_and_obj_list,
        'participants': participants_name_and_obj_list,
        'gen_locs_with_spec_locs': gen_locs_with_spec_locs_list,
        'games': games_name_and_obj_list,
        'known_events': known_events
    }
    return render(request, 'history/timeline_main.html', context)


@login_required
def timeline_create_view(request):
    if request.method == 'POST':
        form = TimelineEventCreateForm(request.POST)
        if form.is_valid():
            event = form.save()
            event.threads.set(form.cleaned_data['threads'])
            event.participants.set(form.cleaned_data['participants'])
            event.informed.set(form.cleaned_data['informed'])
            event.specific_locations.set(form.cleaned_data['specific_locations'])
            event.save()
            messages.info(request, f'Dodano nowe wydarzenie!')
            _next = request.POST.get('next', '/')
            return HttpResponseRedirect(_next)
        else:
            messages.warning(request, 'Popraw poniższy błąd!')

    else:
        form = TimelineEventCreateForm()

    context = {
        'page_title': 'Nowe wydarzenie: Kalendarium',
        'form': form
    }
    return render(request, 'history/timeline_create.html', context)


@login_required
def timeline_all_events_view(request):
    known_events = participated_and_informed_events(request.user.profile.id)
    known_events = list(known_events)

    context = {
        'page_title': 'Pełne Kalendarium',
        'header': 'Opisane tu wydarzenia rozpoczęły swój bieg 20. roku Archonatu Nemetha Samatiana w Ebbonie, '
                  'choć zarodki wielu z nich sięgają znacznie odleglejszych czasów...',
        'events': known_events,
        'seasons_with_styles_dict': SEASONS_WITH_STYLES_DICT,
    }
    return render(request, 'history/timeline_events.html', context)


@login_required
def timeline_thread_view(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id)
    events_by_thread_qs = thread.timeline_events.all()
    known_events = participated_and_informed_events(request.user.profile.id)
    events = list(events_by_thread_qs.distinct() & known_events.distinct())

    context = {
        'page_title': f'{thread.name}',
        'header': f'{thread.name}... Próbujesz sobie przypomnieć, od czego się to wszystko zaczęło?',
        'events': events,
        'seasons_with_styles_dict': SEASONS_WITH_STYLES_DICT,
    }
    if events:
        return render(request, 'history/timeline_events.html', context)
    else:
        return redirect('home:dupa')


@login_required
def timeline_participant_view(request, participant_id):
    participant = get_object_or_404(Profile, id=participant_id)
    events_by_participant_qs = participant.timeline_events_participated.all()
    known_events = participated_and_informed_events(request.user.profile.id)
    events = list(events_by_participant_qs.distinct() & known_events.distinct())

    if request.user.profile == participant:
        text = 'Są czasy, gdy ogarnia Cię zaduma nad Twoim zawikłanym losem...'
    else:
        text = f'{participant.character_name.split(" ", 1)[0]}... Niejedno już razem przeżyliście. Na dobre i na złe...'

    context = {
        'page_title': f'{participant.character_name}',
        'header': text,
        'events': events,
        'seasons_with_styles_dict': SEASONS_WITH_STYLES_DICT,
    }
    if events:
        return render(request, 'history/timeline_events.html', context)
    else:
        return redirect('home:dupa')


@login_required
def timeline_general_location_view(request, gen_loc_id):
    general_location = get_object_or_404(GeneralLocation, id=gen_loc_id)
    events_by_general_location_qs = TimelineEvent.objects.filter(general_location=general_location)
    known_events = participated_and_informed_events(request.user.profile.id)
    events = list(events_by_general_location_qs.distinct() & known_events.distinct())

    context = {
        'page_title': f'{general_location.name}',
        'header': f'{general_location.name}... Zastanawiasz się, jakie piętno wywarła na Twoich losach ta kraina...',
        'events': events,
        'seasons_with_styles_dict': SEASONS_WITH_STYLES_DICT,
    }
    if events:
        return render(request, 'history/timeline_events.html', context)
    else:
        return redirect('home:dupa')


@login_required
def timeline_specific_location_view(request, spec_loc_id):
    specific_location = get_object_or_404(SpecificLocation, id=spec_loc_id)
    events_by_specific_location_qs = specific_location.timeline_events.all()
    known_events = participated_and_informed_events(request.user.profile.id)
    events = list(events_by_specific_location_qs.distinct() & known_events.distinct())

    context = {
        'page_title': f'{specific_location.name}',
        'header': f'{specific_location.name}... Jak to miejsce odcisnęło się na Twoim losie?',
        'events': events,
        'seasons_with_styles_dict': SEASONS_WITH_STYLES_DICT,
    }
    if events:
        return render(request, 'history/timeline_events.html', context)
    else:
        return redirect('home:dupa')


@login_required
def timeline_date_view(request, year, season='0'):
    if season == '0':
        page_title = f'{year}. rok Archonatu Nemetha Samatiana'
        events_qs = TimelineEvent.objects.filter(year=year)
    else:
        if season == '1':
            season_name = 'Wiosna'
        elif season == '2':
            season_name = "Lato"
        elif season == '3':
            season_name = "Jesień"
        else:
            season_name = "Zima"
        events_qs = TimelineEvent.objects.filter(year=year, season=season)
        page_title = f'{season_name} {year}. roku Archonatu Nemetha Samatiana'

    known_events = participated_and_informed_events(request.user.profile.id)
    events = list(events_qs.distinct() & known_events.distinct())

    context = {
        'page_title': page_title,
        'header': f'Nie wydaje się to wcale aż tak dawno temu...',
        'events': events,
        'seasons_with_styles_dict': SEASONS_WITH_STYLES_DICT,
    }
    if events:
        return render(request, 'history/timeline_events.html', context)
    else:
        return redirect('home:dupa')


@login_required
def timeline_game_view(request, game_id):
    game = get_object_or_404(GameSession, id=game_id)
    events_by_game_qs = TimelineEvent.objects.filter(game=game)
    known_events = participated_and_informed_events(request.user.profile.id)
    events = list(events_by_game_qs.distinct() & known_events.distinct())

    context = {
        'page_title': f'{game.title}',
        'header': f'{game.title}... Jak to po kolei było?',
        'events': events,
        'seasons_with_styles_dict': SEASONS_WITH_STYLES_DICT,
    }
    if events:
        return render(request, 'history/timeline_events.html', context)
    else:
        return redirect('home:dupa')


@login_required
def timeline_inform_view(request, event_id):
    event = get_object_or_404(TimelineEvent, id=event_id)

    participants = list(event.participants.all())
    participants_str = ', '.join(p.character_name.split(' ', 1)[0] for p in participants)
    participants_ids = [p.id for p in event.participants.all()]
    old_informed = list(event.informed.all())
    old_informed_ids = [p.id for p in old_informed]
    old_informed_str = ', '.join(p.character_name.split(' ', 1)[0] for p in old_informed)
    allowed = (participants + old_informed)

    if request.method == 'POST':
        form = TimelineEventInformForm(authenticated_user=request.user,
                                       old_informed_ids=old_informed_ids,
                                       participants_ids=participants_ids,
                                       data=request.POST,
                                       instance=event)
        if form.is_valid():
            event = form.save()

            informed = form.cleaned_data['informed']
            informed |= Profile.objects.filter(id__in=old_informed_ids)
            event.informed.set(informed)

            subject = f"[RPG] {request.user.profile} podzielił się z Tobą swoją historią!"
            message = f"{request.user.profile} znów rozprawia o swoich przygodach.\n\n" \
                      f"'{event.date()} rozegrało się co następuje:\n {event.description}\n" \
                      f"Tak było i nie inaczej...'\n" \
                      f"A było to w miejscu: {event.general_location}" \
                      f", a dokładniej: {', '.join(l.name for l in event.specific_locations.all())}.\n\n" \
                      f"Wydarzenie zostało zapisane w Twoim Kalendarium."
            sender = settings.EMAIL_HOST_USER
            receivers = []
            for profile in event.informed.all():
                # exclude previously informed users from mailing to avoid spam
                if profile not in old_informed:
                    receivers.append(profile.user.email)
            if request.user.profile.character_status != 'gm':
                receivers.append('lukas.kozicki@gmail.com')
            send_mail(subject, message, sender, receivers)

            messages.info(request, f'Poinformowałeś wybrane postaci!')
            _next = request.POST.get('next', '/')
            return HttpResponseRedirect(_next)
    else:
        form = TimelineEventInformForm(authenticated_user=request.user,
                                       old_informed_ids=old_informed_ids,
                                       participants_ids=participants_ids)

    context = {
        'page_title': 'Poinformuj o wydarzeniu',
        'form': form,
        'event': event,
        'participants': participants_str,
        'informed': old_informed_str
    }
    if request.user.profile in allowed or request.user.profile.character_status == 'gm':
        return render(request, 'history/timeline_inform.html', context)
    else:
        return redirect('home:dupa')


@login_required
def timeline_note_view(request, event_id):
    event = get_object_or_404(TimelineEvent, id=event_id)

    current_note = None
    participants = list(event.participants.all())
    participants_str = ', '.join(p.character_name.split(' ', 1)[0] for p in participants)
    informed = list(event.informed.all())
    informed_str = ', '.join(p.character_name.split(' ', 1)[0] for p in informed)
    allowed = (participants + informed)

    try:
        current_note = TimelineEventNote.objects.get(event=event, author=request.user)
    except TimelineEventNote.DoesNotExist:
        pass

    if request.method == 'POST':
        form = TimelineEventNoteForm(request.POST, instance=current_note)
        if form.is_valid():
            note = form.save(commit=False)
            note.author = request.user
            note.event = event
            note.save()
            messages.info(request, f'Dodano/zmieniono notatkę!')
            _next = request.POST.get('next', '/')
            return HttpResponseRedirect(_next)

    else:
        form = TimelineEventNoteForm(instance=current_note)

    context = {
        'page_title': 'Przemyślenia',
        'event': event,
        'form': form,
        'participants': participants_str,
        'informed': informed_str
    }
    if request.user.profile in allowed or request.user.profile.character_status == 'gm':
        return render(request, 'history/timeline_note.html', context)
    else:
        return redirect('home:dupa')


@login_required
def timeline_edit_view(request, event_id):
    event = get_object_or_404(TimelineEvent, id=event_id)

    if request.method == 'POST':
        form = TimelineEventEditForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.info(request, f'Zmodyfikowano wydarzenie!')
            _next = request.POST.get('next', '/')
            return HttpResponseRedirect(_next)
    else:
        form = TimelineEventEditForm(instance=event)

    context = {
        'page_title': 'Edycja wydarzenia',
        'form': form
    }
    if request.user.profile.character_status == 'gm':
        return render(request, 'history/timeline_edit.html', context)
    else:
        return redirect('home:dupa')
