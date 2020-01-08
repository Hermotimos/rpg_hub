from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db.models import Count, Prefetch, Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404

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
from rpg_project.utils import query_debugger
from users.models import Profile


# #################### CHRONICLE: model ChronicleEvent ####################


def is_allowed_for_chronicle(profile, chapter_id=0, game_id=0, chronicle_event_id=0, timeline_event_id=0):
    if profile.character_status == 'gm':
        return True
    elif chapter_id:
        if chapter_id in [ch.id for ch in Chapter.objects.filter(
                Q(game_sessions__chronicle_events__participants=profile)
                | Q(game_sessions__chronicle_events__informed=profile))]:
            return True
    elif game_id:
        if game_id in [g.id for g in GameSession.objects.filter(
                Q(chronicle_events__participants=profile) | Q(chronicle_events__informed=profile))]:
            return True
    elif chronicle_event_id:
        if chronicle_event_id in [e.id for e in ChronicleEvent.objects.filter(
                Q(participants=profile) | Q(informed=profile))]:
            return True
    elif timeline_event_id:
        if timeline_event_id in [e.id for e in TimelineEvent.objects.filter(
                Q(participants=profile) | Q(informed=profile))]:
            return True
    else:
        return False


@query_debugger
@login_required
def chronicle_main_view(request):
    profile = request.user.profile

    if request.user.profile.character_status == 'gm':
        chapters = Chapter.objects.prefetch_related('game_sessions')
    else:
        events = (profile.chronicle_events_participated.all() | profile.chronicle_events_informed.all())\
            .distinct()

        games = GameSession.objects.filter(chronicle_events__in=events)\
            .distinct()\
            .prefetch_related(Prefetch('chronicle_events', queryset=events))

        chapters = Chapter.objects\
            .prefetch_related(Prefetch('game_sessions', queryset=games))\
            .filter(game_sessions__in=games).distinct()

    context = {
        'page_title': 'Kronika',
        'chapters': chapters
    }
    return render(request, 'history/chronicle_main.html', context)


@query_debugger
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


@query_debugger
@login_required
def chronicle_all_chapters_view(request):
    profile = request.user.profile

    if profile.character_status == 'gm':
        chapters = Chapter.objects.prefetch_related(
            'game_sessions__chronicle_events__informed',
            'game_sessions__chronicle_events__pictures',
            'game_sessions__chronicle_events__notes__author',
            'game_sessions__chronicle_events__debate__topic'
        )
    else:
        events = (profile.chronicle_events_participated.all() | profile.chronicle_events_informed.all())\
            .distinct()\
            .select_related('debate__topic')\
            .prefetch_related('informed', 'pictures', 'notes__author')

        games = GameSession.objects\
            .filter(chronicle_events__in=events)\
            .distinct()\
            .prefetch_related(Prefetch('chronicle_events', queryset=events))

        chapters = Chapter.objects\
            .prefetch_related(Prefetch('game_sessions', queryset=games))\
            .filter(game_sessions__in=games)\
            .distinct()

    context = {
        'page_title': 'Pełna kronika',
        'chapters': chapters,
        'profile': profile,
    }
    return render(request, 'history/chronicle_all_chapters.html', context)


@query_debugger
@login_required
def chronicle_one_chapter_view(request, chapter_id):
    profile = request.user.profile
    chapter = get_object_or_404(Chapter, id=chapter_id)

    if profile.character_status == 'gm':
        games = chapter.game_sessions.prefetch_related(
            'chronicle_events__informed',
            'chronicle_events__pictures',
            'chronicle_events__notes__author',
            'chronicle_events__debate__topic'
            )
    else:
        events = (profile.chronicle_events_participated.all() | profile.chronicle_events_informed.all())\
            .distinct()\
            .select_related('debate__topic')\
            .prefetch_related('informed', 'pictures', 'notes__author')\
            .filter(game__chapter=chapter_id)

        games = chapter.game_sessions\
            .filter(chronicle_events__in=events)\
            .distinct()\
            .prefetch_related(Prefetch('chronicle_events', queryset=events))

    context = {
        'page_title': chapter.title,
        'games': games,
    }
    if is_allowed_for_chronicle(profile, chapter_id=chapter_id):
        return render(request, 'history/chronicle_one_chapter.html', context)
    else:
        return redirect('home:dupa')


@query_debugger
@login_required
def chronicle_one_game_view(request, game_id, timeline_event_id):
    profile = request.user.profile
    game = get_object_or_404(GameSession, id=game_id)
    event = TimelineEvent.objects.none()

    if timeline_event_id != '0':
        event = TimelineEvent.objects.get(id=timeline_event_id)

    if profile.character_status == 'gm':
        events = game.chronicle_events.all()\
            .select_related('debate__topic')\
            .prefetch_related('informed', 'pictures', 'notes__author')
    else:
        events = game.chronicle_events\
            .filter(Q(informed=profile) | Q(participants=profile))\
            .distinct()\
            .select_related('debate__topic') \
            .prefetch_related('informed', 'pictures', 'notes__author')

    context = {
        'page_title': game.title,
        'events': events,
    }
    if is_allowed_for_chronicle(profile, game_id=game_id):
        return render(request, 'history/chronicle_one_game.html', context)
    elif event and profile in event.informed.all():
        return redirect('history:chronicle-gap', timeline_event_id=timeline_event_id)
    else:
        return redirect('home:dupa')


@query_debugger
@login_required
def chronicle_inform_view(request, event_id):
    profile = request.user.profile
    event = get_object_or_404(ChronicleEvent, id=event_id)

    participants = event.participants.all()
    old_informed = event.informed.all()

    if request.method == 'POST':
        form = ChronicleEventInformForm(authenticated_user=request.user,
                                        old_informed=old_informed,
                                        participants=participants,
                                        data=request.POST,
                                        instance=event)
        if form.is_valid():
            event = form.save()

            new_informed = form.cleaned_data['informed']
            event.informed.add(*list(new_informed))

            subject = f"[RPG] {profile} podzielił się z Tobą swoją historią!"
            message = f"{profile} znów rozprawia o swoich przygodach.\n\n" \
                      f"Podczas przygody '{event.game.title}' rozegrało się co następuje:\n{event.description}\n" \
                      f"Tak było i nie inaczej...\n\n" \
                      f"Wydarzenie zostało zapisane w Twojej Kronice: " \
                      f"{request.get_host()}/history/chronicle/one-game:{event.game.id}/"
            sender = settings.EMAIL_HOST_USER
            receivers = []
            for profile in new_informed:
                receivers.append(profile.user.email)
            if profile.character_status != 'gm':
                receivers.append('lukas.kozicki@gmail.com')
            send_mail(subject, message, sender, receivers)

            messages.info(request, f'Poinformowałeś wybrane postaci!')
            _next = request.POST.get('next', '/')
            return HttpResponseRedirect(_next)
    else:
        form = ChronicleEventInformForm(authenticated_user=request.user,
                                        old_informed=old_informed,
                                        participants=participants)

    context = {
        'page_title': 'Poinformuj o wydarzeniu',
        'form': form,
        'event': event,
    }
    if is_allowed_for_chronicle(profile, chronicle_event_id=event_id):
        return render(request, 'history/chronicle_inform.html', context)
    else:
        return redirect('home:dupa')


@query_debugger
@login_required
def chronicle_note_view(request, event_id):
    profile = request.user.profile
    event = get_object_or_404(ChronicleEvent, id=event_id)
    current_note = None

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
    }
    if is_allowed_for_chronicle(profile, chronicle_event_id=event_id):
        return render(request, 'history/chronicle_note.html', context)
    else:
        return redirect('home:dupa')


@query_debugger
@login_required
def chronicle_edit_view(request, event_id):
    profile = request.user.profile
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
    if profile.character_status == 'gm':
        return render(request, 'history/chronicle_edit.html', context)
    else:
        return redirect('home:dupa')


def chronicle_gap_view(request, timeline_event_id):
    timeline_event = get_object_or_404(TimelineEvent, id=timeline_event_id)
    participants_and_informed = (timeline_event.participants.all() | (timeline_event.informed.all())).distinct()
    participants_and_informed_str = ', '.join(p.character_name.split(' ', 1)[0] for p in participants_and_informed)

    context = {
        'page_title': 'Luka w Kronice',
        'participants_and_informed': participants_and_informed_str
    }
    return render(request, 'history/chronicle_gap.html', context)


# #################### TIMELINE: model TimelineEvent ####################


SEASONS_WITH_STYLES_DICT = {
    '1': 'season-spring',
    '2': 'season-summer',
    '3': 'season-autumn',
    '4': 'season-winter'
}


@query_debugger
@login_required
def timeline_main_view(request):
    profile = request.user.profile

    if profile.character_status == 'gm':
        threads = Thread.objects.all()
        participants = Profile.objects.filter(character_status__in=['active_player', 'inactive_player', 'dead_player'])
        gen_locs = GeneralLocation.objects.all().prefetch_related('specific_locations')
        games = GameSession.objects.annotate(num_events=Count('timeline_events')).filter(num_events__gt=0)
        events = TimelineEvent.objects.all()
    else:
        threads = Thread.objects\
            .filter(Q(timeline_events__participants=profile) | Q(timeline_events__informed=profile))\
            .distinct()
        participants = Profile.objects\
            .filter(character_status__in=['active_player', 'inactive_player', 'dead_player'])\
            .filter(timeline_events_participated__in=profile.timeline_events_participated.all())\
            .distinct()
        spec_locs = SpecificLocation.objects \
            .filter(Q(timeline_events__participants=profile) | Q(timeline_events__informed=profile)) \
            .distinct()
        gen_locs = GeneralLocation.objects\
            .filter(specific_locations__in=spec_locs)\
            .distinct()\
            .prefetch_related(Prefetch('specific_locations', queryset=spec_locs))
        games = GameSession.objects \
            .filter(Q(timeline_events__participants=profile) | Q(timeline_events__informed=profile)) \
            .distinct()
        events = (profile.timeline_events_participated.all() | profile.timeline_events_informed.all())\
            .distinct()

    years = list({y for y in (e.year for e in events)})
    years.sort()
    years_with_seasons_dict = {}
    for y in years:
        seasons = list({e.season for e in events if e.year == y})
        seasons.sort()
        years_with_seasons_dict[y] = seasons

    context = {
        'page_title': 'Kalendarium',
        'seasons_with_styles_dict': SEASONS_WITH_STYLES_DICT,
        'years_with_seasons_dict': years_with_seasons_dict,
        'threads': threads,
        'participants': participants,
        'gen_locs': gen_locs,
        'games': games,
    }
    return render(request, 'history/timeline_main.html', context)


@query_debugger
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


@query_debugger
@login_required
def timeline_all_events_view(request):
    profile = request.user.profile

    if profile.character_status == 'gm':
        events = TimelineEvent.objects.all()
    else:
        events = (profile.timeline_events_participated.all() | profile.timeline_events_informed.all())\
            .distinct()

    events = events\
        .select_related('game')\
        .prefetch_related('threads', 'participants', 'informed', 'general_locations', 'specific_locations', 'notes__author')

    context = {
        'page_title': 'Pełne Kalendarium',
        'header': 'Opisane tu wydarzenia rozpoczęły swój bieg 20. roku Archonatu Nemetha Samatiana w Ebbonie, '
                  'choć zarodki wielu z nich sięgają znacznie odleglejszych czasów...',
        'events': events,
        'seasons_with_styles_dict': SEASONS_WITH_STYLES_DICT,
    }
    return render(request, 'history/timeline_events.html', context)


@query_debugger
@login_required
def timeline_thread_view(request, thread_id):
    profile = request.user.profile
    thread = get_object_or_404(Thread, id=thread_id)

    if profile.character_status == 'gm':
        events = TimelineEvent.objects.filter(threads=thread)
    else:
        events = (profile.timeline_events_participated.all() | profile.timeline_events_informed.all())\
            .filter(threads=thread)\
            .distinct()

    events = events\
        .select_related('game')\
        .prefetch_related('threads', 'participants', 'informed', 'general_locations', 'specific_locations', 'notes__author')

    context = {
        'page_title': thread.name,
        'header': f'{thread.name}... Próbujesz sobie przypomnieć, od czego się to wszystko zaczęło?',
        'events': events,
        'seasons_with_styles_dict': SEASONS_WITH_STYLES_DICT,
    }
    if events:
        return render(request, 'history/timeline_events.html', context)
    else:
        return redirect('home:dupa')


@query_debugger
@login_required
def timeline_participant_view(request, participant_id):
    profile = request.user.profile
    participant = get_object_or_404(Profile, id=participant_id)

    if profile.character_status == 'gm':
        events = TimelineEvent.objects.filter(participants=participant_id)
    else:
        events = (profile.timeline_events_participated.all() | profile.timeline_events_informed.all())\
            .filter(participants=participant_id)\
            .distinct()

    events = events\
        .select_related('game')\
        .prefetch_related('threads', 'participants', 'informed', 'general_locations', 'specific_locations', 'notes__author')

    if profile == participant:
        header = 'Są czasy, gdy ogarnia Cię zaduma nad Twoim zawikłanym losem...'
    else:
        header = f'{participant.character_name.split(" ", 1)[0]}... Niejedno razem przeżyliście. Na dobre i na złe...'

    context = {
        'page_title': participant.character_name,
        'header': header,
        'events': events,
        'seasons_with_styles_dict': SEASONS_WITH_STYLES_DICT,
    }
    if events:
        return render(request, 'history/timeline_events.html', context)
    else:
        return redirect('home:dupa')


@query_debugger
@login_required
def timeline_general_location_view(request, gen_loc_id):
    profile = request.user.profile
    general_location = get_object_or_404(GeneralLocation, id=gen_loc_id)

    if profile.character_status == 'gm':
        events = TimelineEvent.objects.filter(general_locations=gen_loc_id)
    else:
        events = (profile.timeline_events_participated.all() | profile.timeline_events_informed.all())\
            .filter(general_locations=gen_loc_id)\
            .distinct()

    events = events\
        .select_related('game')\
        .prefetch_related('threads', 'participants', 'informed', 'general_locations', 'specific_locations', 'notes__author')

    context = {
        'page_title': general_location.name,
        'header': f'{general_location.name}... Zastanawiasz się, jakie piętno wywarła na Twoich losach ta kraina...',
        'events': events,
        'seasons_with_styles_dict': SEASONS_WITH_STYLES_DICT,
    }
    if events:
        return render(request, 'history/timeline_events.html', context)
    else:
        return redirect('home:dupa')


@query_debugger
@login_required
def timeline_specific_location_view(request, spec_loc_id):
    profile = request.user.profile
    specific_location = get_object_or_404(SpecificLocation, id=spec_loc_id)

    if profile.character_status == 'gm':
        events = TimelineEvent.objects.filter(specific_locations=spec_loc_id)
    else:
        events = (profile.timeline_events_participated.all() | profile.timeline_events_informed.all())\
            .filter(specific_locations=spec_loc_id)\
            .distinct()

    events = events\
        .select_related('game')\
        .prefetch_related('threads', 'participants', 'informed', 'general_locations', 'specific_locations', 'notes__author')

    context = {
        'page_title': specific_location.name,
        'header': f'{specific_location.name}... Jak to miejsce odcisnęło się na Twoim losie?',
        'events': events,
        'seasons_with_styles_dict': SEASONS_WITH_STYLES_DICT,
    }
    if events:
        return render(request, 'history/timeline_events.html', context)
    else:
        return redirect('home:dupa')


@query_debugger
@login_required
def timeline_date_view(request, year, season='0'):
    profile = request.user.profile

    if profile.character_status == 'gm':
        events = TimelineEvent.objects.all()
    else:
        events = (profile.timeline_events_participated.all() | profile.timeline_events_informed.all())\
            .distinct()

    events = events\
        .select_related('game')\
        .prefetch_related('threads', 'participants', 'informed', 'general_locations', 'specific_locations', 'notes__author')

    if season == '0':
        events = events.filter(year=year)
        page_title = f'{year}. rok Archonatu Nemetha Samatiana'
    else:
        if season == '1':
            season_name = 'Wiosna'
        elif season == '2':
            season_name = "Lato"
        elif season == '3':
            season_name = "Jesień"
        else:
            season_name = "Zima"
        events = events.filter(year=year, season=season)
        page_title = f'{season_name} {year}. roku Archonatu Nemetha Samatiana'

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


@query_debugger
@login_required
def timeline_game_view(request, game_id):
    profile = request.user.profile
    game = get_object_or_404(GameSession, id=game_id)

    if profile.character_status == 'gm':
        events = TimelineEvent.objects.filter(game=game_id)
    else:
        events = (profile.timeline_events_participated.all() | profile.timeline_events_informed.all())\
            .filter(game=game_id)\
            .distinct()

    events = events\
        .select_related('game')\
        .prefetch_related('threads', 'participants', 'informed', 'general_locations', 'specific_locations', 'notes__author')

    context = {
        'page_title': game.title,
        'header': f'{game.title}... Jak to po kolei było?',
        'events': events,
        'seasons_with_styles_dict': SEASONS_WITH_STYLES_DICT,
    }
    if events:
        return render(request, 'history/timeline_events.html', context)
    else:
        return redirect('home:dupa')


@query_debugger
@login_required
def timeline_inform_view(request, event_id):
    profile = request.user.profile
    event = get_object_or_404(TimelineEvent, id=event_id)

    spec_locs = event.specific_locations.all()
    gen_locs = event.general_locations\
        .prefetch_related(Prefetch('specific_locations', queryset=spec_locs, to_attr='filtered_spec_locs'))
    gen_locs_and_spec_locs_dict = {}
    for gen_loc in gen_locs:
        gen_locs_and_spec_locs_dict[gen_loc.name] = ', '.join(spec_loc.name for spec_loc in gen_loc.filtered_spec_locs)

    participants = event.participants.all()
    participants_ids = [p.id for p in participants]
    old_informed = event.informed.all()
    old_informed_ids = [p.id for p in old_informed]

    if request.method == 'POST':
        form = TimelineEventInformForm(authenticated_user=request.user,
                                       old_informed_ids=old_informed_ids,
                                       participants_ids=participants_ids,
                                       data=request.POST,
                                       instance=event)
        if form.is_valid():
            # event = form.save()
            informed_new = form.cleaned_data['informed']
            event.informed.add(*list(informed_new))

            subject = f"[RPG] {profile} podzielił się z Tobą swoją historią!"
            message = f"{profile} znów rozprawia o swoich przygodach.\n\n" \
                      f"'{event.date()} rozegrało się co następuje:\n {event.description}\n" \
                      f"Tak było i nie inaczej...'\n" \
                      f"A było to w miejscu: {', '.join(l.name for l in event.general_locations.all())}" \
                      f", a dokładniej: {', '.join(l.name for l in event.specific_locations.all())}.\n\n" \
                      f"Wydarzenie zostało zapisane w Twoim Kalendarium."
            sender = settings.EMAIL_HOST_USER
            receivers = []
            for new_profile in informed_new:
                receivers.append(new_profile.user.email)
            if profile.character_status != 'gm':
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
        'gen_locs_and_spec_locs_dict': gen_locs_and_spec_locs_dict,
        'participants': participants,
        'informed': old_informed
    }
    if profile in (event.participants.all() | event.informed.all()) or profile.character_status == 'gm':
        return render(request, 'history/timeline_inform.html', context)
    else:
        return redirect('home:dupa')


@query_debugger
@login_required
def timeline_note_view(request, event_id):
    profile = request.user.profile
    event = get_object_or_404(TimelineEvent, id=event_id)
    current_note = None

    spec_locs = event.specific_locations.all()
    gen_locs = event.general_locations\
        .prefetch_related(Prefetch('specific_locations', queryset=spec_locs, to_attr='filtered_spec_locs'))
    gen_locs_and_spec_locs_dict = {}
    for gen_loc in gen_locs:
        gen_locs_and_spec_locs_dict[gen_loc.name] = ', '.join(spec_loc.name for spec_loc in gen_loc.filtered_spec_locs)

    participants = event.participants.all()
    informed = event.informed.all()

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
        'gen_locs_and_spec_locs_dict': gen_locs_and_spec_locs_dict,
        'participants': participants,
        'informed': informed
    }
    if profile in (event.participants.all() | event.informed.all()) or profile.character_status == 'gm':
        return render(request, 'history/timeline_note.html', context)
    else:
        return redirect('home:dupa')


@query_debugger
@login_required
def timeline_edit_view(request, event_id):
    profile = request.user.profile
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
    if profile.character_status == 'gm':
        return render(request, 'history/timeline_edit.html', context)
    else:
        return redirect('home:dupa')
