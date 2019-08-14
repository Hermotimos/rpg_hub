from django.shortcuts import render, get_object_or_404
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


# #################### TIMELINE: model TimelineEvent ####################

SEASONS_WITH_STYLES_DICT = {
    '1': 'season-spring',
    '2': 'season-summer',
    '3': 'season-autumn',
    '4': 'season-winter'
}


def participated_or_informed_events(profile_id):
    profile = Profile.objects.get(id=profile_id)
    if profile.character_status == 'gm':
        known_qs = TimelineEvent.objects.all()
    else:
        participated_qs = Profile.objects.get(id=profile_id).events_participated.all()
        informed_qs = Profile.objects.get(id=profile_id).events_informed.all()
        known_qs = (participated_qs | informed_qs).distinct()
    return known_qs


@login_required
def timeline_main_view(request):
    known_events = participated_or_informed_events(request.user.profile.id)

    # repetitive interations over known_events.all():
    years_set = set()
    threads_querysets_list = []
    participants_querysets_list = []
    spec_locs_querysets_list = []
    gen_locs_set = set()
    games_set = set()
    for event in known_events.all():
        years_set.add(event.year)
        threads_querysets_list.append(event.threads.all())
        participants_querysets_list.append(event.participants.all())
        spec_locs_querysets_list.append(event.specific_locations.all())
        gen_locs_set.add(event.general_location)
        games_set.add(event.game_no)

    # years
    # years_set = {e.year for e in known_events.all()}
    years_sorted_list = list(years_set)
    years_sorted_list.sort()

    # years with their seasons
    years_with_seasons_dict = {}
    for y in years_sorted_list:
        seasons_set = {e.season for e in known_events.all() if e.year == y}
        seasons_sorted_list = list(seasons_set)
        seasons_sorted_list.sort()
        years_with_seasons_dict[y] = seasons_sorted_list

    # threads
    threads_set = set()
    # threads_querysets_list = [event.threads.all() for event in known_events]
    for qs in threads_querysets_list:
        for th in qs:
            threads_set.add(th)
    threads_name_and_obj_list = [(t.name, t) for t in threads_set]
    threads_name_and_obj_list.sort()

    # participants
    participants_set = set()
    # participants_querysets_list = [event.participants.all() for event in known_events]
    for qs in participants_querysets_list:
        for p in qs:
            participants_set.add(p)
    participants_name_and_obj_list = [(t.character_name, t) for t in participants_set]
    participants_name_and_obj_list.sort()

    # specific locations
    spec_locs_set = set()
    # spec_locs_querysets_list = [event.specific_locations.all() for event in known_events]
    for qs in spec_locs_querysets_list:
        for sl in qs:
            spec_locs_set.add(sl)
    spec_locs_name_and_obj_list = [(t.name, t) for t in spec_locs_set]
    spec_locs_name_and_obj_list.sort()

    # general locations with their specific locations: LEFT UNSORTED TO REFLECT SUBSEQUENT GENERAL LOCATIONS IN GAME
    # gen_locs_set = {event.general_location for event in known_events}
    gen_locs_with_spec_locs_list = []
    for gl in gen_locs_set:
        gen_loc_with_spec_locs_list = [gl, [sl for sl in spec_locs_name_and_obj_list if sl[1].general_location == gl]]
        gen_locs_with_spec_locs_list.append(gen_loc_with_spec_locs_list)

    # games
    # games_set = {event.game_no for event in known_events}
    games_sorted_list = list(games_set)
    games_sorted_list.sort(key=lambda game: game.game_no)
    games_name_and_obj_list = [(g.title, g) for g in games_sorted_list]
    # games_name_and_obj_list.

    context = {
        'page_title': 'Kalendarium',
        'seasons_with_styles_dict': SEASONS_WITH_STYLES_DICT,
        'years_with_seasons_dict': years_with_seasons_dict,
        'threads': threads_name_and_obj_list,
        'participants': participants_name_and_obj_list,
        'gen_locs_with_spec_locs': gen_locs_with_spec_locs_list,
        'games': games_name_and_obj_list,
    }
    return render(request, 'history/timeline_main.html', context)


@login_required
def timeline_all_events_view(request):
    known_events = participated_or_informed_events(request.user.profile.id)
    queryset = known_events
    context = {
        'page_title': 'Pełne Kalendarium',
        'header': 'Opisane tu wydarzenia rozpoczęły swój bieg 20. roku Archonatu Nemetha Samatiana w Ebbonie, '
                  'choć zarodki wielu z nich sięgają znacznie odleglejszych czasów...',
        'queryset': queryset,
        'seasons_with_styles_dict': SEASONS_WITH_STYLES_DICT,
    }
    return render(request, 'history/timeline_events.html', context)


@login_required
def timeline_thread_view(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id)
    events_by_thread_qs = thread.events.all()
    known_events = participated_or_informed_events(request.user.profile.id)
    queryset = set(events_by_thread_qs) & set(known_events)
    context = {
        'page_title': f'Kalendarium: {thread.name}',
        'header': f'{thread.name}... Próbujesz sobie przypomnieć, od czego się to wszystko zaczęło?',
        'queryset': queryset,
        'seasons_with_styles_dict': SEASONS_WITH_STYLES_DICT,
    }
    return render(request, 'history/timeline_events.html', context)


@login_required
def timeline_participant_view(request, participant_id):
    participant = get_object_or_404(Profile, id=participant_id)
    events_by_participant_qs = participant.events_participated.all()
    known_events = participated_or_informed_events(request.user.profile.id)
    queryset = set(events_by_participant_qs) & set(known_events)

    if request.user.profile == participant:
        text = 'Są czasy, gdy ogarnia Cię zaduma nad Twoim zawikłanym losem...'
    else:
        text = f'{participant.character_name.split(" ", 1)[0]}... Niejedno już razem przeżyliście. Na dobre i na złe...'

    context = {
        'page_title': f'Kalendarium: {participant.character_name}',
        'header': text,
        'queryset': queryset,
        'seasons_with_styles_dict': SEASONS_WITH_STYLES_DICT,
    }
    return render(request, 'history/timeline_events.html', context)


@login_required
def timeline_general_location_view(request, gen_loc_id):
    general_location = get_object_or_404(GeneralLocation, id=gen_loc_id)
    events_by_general_location_qs = TimelineEvent.objects.filter(general_location=general_location)
    known_events = participated_or_informed_events(request.user.profile.id)
    queryset = set(events_by_general_location_qs) & set(known_events)
    context = {
        'page_title': f'Kalendarium: {general_location.name}',
        'header': f'{general_location.name}... Zastanawiasz się, jakie piętno wywarła na Twoich losach ta kraina...',
        'queryset': queryset,
        'seasons_with_styles_dict': SEASONS_WITH_STYLES_DICT,
    }
    return render(request, 'history/timeline_events.html', context)


@login_required
def timeline_specific_location_view(request, spec_loc_id):
    specific_location = get_object_or_404(SpecificLocation, id=spec_loc_id)
    events_by_specific_location_qs = specific_location.events.all()
    known_events = participated_or_informed_events(request.user.profile.id)
    queryset = set(events_by_specific_location_qs) & set(known_events)
    context = {
        'page_title': f'Kalendarium: {specific_location.name}',
        'header': f'{specific_location.name}... Jak to miejsce odcisnęło się na Twoim losie?',
        'queryset': queryset,
        'seasons_with_styles_dict': SEASONS_WITH_STYLES_DICT,
    }
    return render(request, 'history/timeline_events.html', context)


@login_required
def timeline_date_view(request, year, season='0'):
    if season == '0':
        page_title = f'Kalendarium: {year}. rok Archonatu Nemetha Samatiana'
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
        page_title = f'Kalendarium: {season_name} {year}. roku Archonatu Nemetha Samatiana'

    known_events = participated_or_informed_events(request.user.profile.id)
    queryset = set(events_qs) & set(known_events)

    context = {
        'page_title': page_title,
        'header': f'Nie wydaje się to wcale aż tak dawno temu...',
        'queryset': queryset,
        'seasons_with_styles_dict': SEASONS_WITH_STYLES_DICT,
    }
    return render(request, 'history/timeline_events.html', context)


@login_required
def timeline_game_view(request, game_id):
    game = get_object_or_404(GameSession, id=game_id)
    events_by_game_no_qs = TimelineEvent.objects.filter(game_no=game)
    known_events = participated_or_informed_events(request.user.profile.id)
    queryset = set(events_by_game_no_qs) & set(known_events)
    context = {
        'page_title': f'Kalendarium: {game.title}',
        'header': f'{game.title}... Jak to po kolei było?',
        'queryset': queryset,
        'seasons_with_styles_dict': SEASONS_WITH_STYLES_DICT,
    }
    return render(request, 'history/timeline_events.html', context)


@login_required
def timeline_create_view(request):
    if request.method == 'POST':
        form = TimelineEventCreateForm(request.POST or None)
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
def timeline_inform_view(request, event_id):
    obj = get_object_or_404(TimelineEvent, id=event_id)

    participants_str = ', '.join(p.character_name.split(' ', 1)[0] for p in obj.participants.all())
    participants_ids = [p.id for p in obj.participants.all()]
    old_informed = obj.informed.all()[::1]                  # enforces evaluation of lazy Queryset for message
    old_informed_ids = [p.id for p in old_informed]
    old_informed_str = ', '.join(p.character_name.split(' ', 1)[0] for p in old_informed)

    if request.method == 'POST':
        form = TimelineEventInformForm(authenticated_user=request.user,
                                       old_informed_ids=old_informed_ids,
                                       participants_ids=participants_ids,
                                       data=request.POST,
                                       instance=obj)
        if form.is_valid():
            event = form.save()

            informed = form.cleaned_data['informed']
            informed |= Profile.objects.filter(id__in=old_informed_ids)
            event.informed.set(informed)

            subject = f"[RPG] {request.user.profile} podzielił się z Tobą swoją historią!"
            message = f"{request.user.profile} znów rozprawia o swoich przygodach.\n\n" \
                      f"'{obj.date()} rozegrało się co następuje:\n {obj.description}\n" \
                      f"Tak było i nie inaczej...'\n" \
                      f"A było to w miejscu: {obj.general_location}" \
                      f", a dokładniej: {', '.join(l.name for l in obj.specific_locations.all())}.\n\n" \
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
        'event': obj,
        'participants': participants_str,
        'informed': old_informed_str
    }
    return render(request, 'history/timeline_inform.html', context)


@login_required
def timeline_note_view(request, event_id):
    obj = get_object_or_404(TimelineEvent, id=event_id)

    current_note = None
    participants = ', '.join(p.character_name.split(' ', 1)[0] for p in obj.participants.all())
    informed = ', '.join(p.character_name.split(' ', 1)[0] for p in obj.informed.all())

    try:
        current_note = TimelineEventNote.objects.get(event=obj, author=request.user)
    except TimelineEventNote.DoesNotExist:
        pass

    if request.method == 'POST':
        form = TimelineEventNoteForm(request.POST, instance=current_note)
        if form.is_valid():
            note = form.save(commit=False)
            note.author = request.user
            note.event = obj
            note.save()
            messages.info(request, f'Dodano/zmieniono notatkę!')
            _next = request.POST.get('next', '/')
            return HttpResponseRedirect(_next)

    else:
        form = TimelineEventNoteForm(instance=current_note)

    context = {
        'page_title': 'Notatka',
        'event': obj,
        'form': form,
        'participants': participants,
        'informed': informed
    }
    return render(request, 'history/timeline_note.html', context)


@login_required
def timeline_edit_view(request, event_id):
    obj = get_object_or_404(TimelineEvent, id=event_id)

    if request.method == 'POST':
        form = TimelineEventEditForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.info(request, f'Zmodyfikowano wydarzenie!')
            _next = request.POST.get('next', '/')
            return HttpResponseRedirect(_next)
    else:
        form = TimelineEventEditForm(instance=obj)

    context = {
        'page_title': 'Edycja wydarzenia',
        'form': form
    }
    return render(request, 'history/timeline_edit.html', context)


# #################### CHRONICLE: model ChronicleEvent ####################


def is_allowed_game(_game, profile):
    for event in _game.described_events.all():
        if profile in event.participants.all() or profile in event.informed.all() or profile.character_status == 'gm':
            return True
    return False


@login_required
def chronicle_main_view(request):
    games = GameSession.objects.all()
    allowed_bios_list = [g for g in games if is_allowed_game(g, request.user.profile) and g.game_no < 0]
    allowed_games_list = [g for g in games if is_allowed_game(g, request.user.profile) and g.game_no > 0]

    context = {
        'page_title': 'Historia',
        'allowed_bios_list': allowed_bios_list,
        'allowed_games_list': allowed_games_list
    }
    return render(request, 'history/chronicle_main.html', context)


@login_required
def chronicle_all_chapters_view(request):
    games = GameSession.objects.all()
    allowed_bios_list = [g for g in games if is_allowed_game(g, request.user.profile) and g.game_no < 0]
    allowed_games_list = [g for g in games if is_allowed_game(g, request.user.profile) and g.game_no > 0]

    context = {
        'page_title': 'Pełna historia drużyny',
        'allowed_bios_list': allowed_bios_list,
        'allowed_games_list': allowed_games_list
    }
    return render(request, 'history/chronicle_all_chapters.html', context)


@login_required
def chronicle_one_chapter_view(request, game_id):
    obj = get_object_or_404(GameSession, id=game_id)

    if ':' in obj.title:
        page_title = f'{obj.title.split(": ", 1)[0]}:\n"{obj.title.split(": ", 1)[1]}"'
    else:
        page_title = obj.title

    context = {
        'page_title': page_title,
        'game': obj
    }
    return render(request, 'history/chronicle_one_chapter.html', context)


@login_required
def chronicle_create_view(request):
    if request.method == 'POST':
        form = ChronicleEventCreateForm(request.POST or None)
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
        'page_title': 'Nowe wydarzenie: Historia',
        'form': form
    }
    return render(request, 'history/chronicle_create.html', context)


@login_required
def chronicle_inform_view(request, event_id):
    obj = get_object_or_404(ChronicleEvent, id=event_id)

    participants_str = ', '.join(p.character_name.split(' ', 1)[0] for p in obj.participants.all())
    participants_ids = [p.id for p in obj.participants.all()]
    old_informed = obj.informed.all()[::1]                  # enforces evaluation of lazy Queryset for message
    old_informed_ids = [p.id for p in old_informed]
    old_informed_str = ', '.join(p.character_name.split(' ', 1)[0] for p in old_informed)

    if request.method == 'POST':
        form = ChronicleEventInformForm(authenticated_user=request.user,
                                        old_informed_ids=old_informed_ids,
                                        participants_ids=participants_ids,
                                        data=request.POST,
                                        instance=obj)
        if form.is_valid():
            event = form.save()

            informed = form.cleaned_data['informed']
            informed |= Profile.objects.filter(id__in=old_informed_ids)
            event.informed.set(informed)

            subject = f"[RPG] {request.user.profile} podzielił się z Tobą swoją historią!"
            message = f"{request.user.profile} znów rozprawia o swoich przygodach.\n" \
                      f"{', '.join(p.character_name for p in form.cleaned_data['informed'])}\n\n" \
                      f"Podczas przygody '{obj.game_no.title}' rozegrało się co następuje:\n {obj.description}\n" \
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
        'event': obj,
        'participants': participants_str,
        'informed': old_informed_str
    }
    return render(request, 'history/chronicle_inform.html', context)


@login_required
def chronicle_note_view(request, event_id):
    obj = get_object_or_404(ChronicleEvent, id=event_id)

    current_note = None
    participants = ', '.join(p.character_name.split(' ', 1)[0] for p in obj.participants.all())
    informed = ', '.join(p.character_name.split(' ', 1)[0] for p in obj.informed.all())

    try:
        current_note = ChronicleEventNote.objects.get(event=obj, author=request.user)
    except ChronicleEventNote.DoesNotExist:
        pass

    if request.method == 'POST':
        form = ChronicleEventNoteForm(request.POST, instance=current_note)
        if form.is_valid():
            note = form.save(commit=False)
            note.author = request.user
            note.event = obj
            note.save()
            messages.info(request, f'Dodano/zmieniono notatkę!')
            _next = request.POST.get('next', '/')
            return HttpResponseRedirect(_next)
    else:
        form = ChronicleEventNoteForm(instance=current_note)

    context = {
        'page_title': 'Notatka',
        'event': obj,
        'form': form,
        'participants': participants,
        'informed': informed
    }
    return render(request, 'history/chronicle_note.html', context)


@login_required
def chronicle_edit_view(request, event_id):
    obj = get_object_or_404(ChronicleEvent, id=event_id)

    if request.method == 'POST':
        form = ChronicleEventEditForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.info(request, f'Zmodyfikowano wydarzenie!')
            _next = request.POST.get('next', '/')
            return HttpResponseRedirect(_next)
    else:
        form = ChronicleEventEditForm(instance=obj)

    context = {
        'page_title': 'Edycja wydarzenia',
        'form': form
    }
    return render(request, 'history/chronicle_edit.html', context)
