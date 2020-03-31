from django.contrib import messages
from django.contrib.auth.decorators import login_required
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
                           TimelineEventEditForm,
                           TimelineEventNoteForm,
                           ChronicleEventNoteForm,
                           ChronicleEventCreateForm,
                           ChronicleEventEditForm)
from rpg_project.utils import query_debugger, send_emails
from users.models import Profile


# #################### CHRONICLE: model ChronicleEvent ####################


def is_allowed_for_chronicle(profile, chapter_id=0, game_id=0,
                             chronicle_event_id=0, timeline_event_id=0):
    
    if profile.status == 'gm':
        return True
    elif chapter_id:
        if chapter_id in [ch.id for ch in Chapter.objects.filter(
                Q(game_sessions__chronicle_events__participants=profile)
                | Q(game_sessions__chronicle_events__informed=profile))]:
            return True
    elif game_id:
        if game_id in [g.id for g in GameSession.objects.filter(
                Q(chronicle_events__participants=profile)
                | Q(chronicle_events__informed=profile))]:
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

    if request.user.profile.status == 'gm':
        chapters = Chapter.objects.prefetch_related('game_sessions')
    else:
        events = (profile.chronicle_events_participated.all()
                  | profile.chronicle_events_informed.all())\
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
    profile = request.user.profile

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
    if profile.status == 'gm':
        return render(request, 'history/chronicle_create.html', context)
    else:
        return redirect('home:dupa')


@query_debugger
@login_required
def chronicle_all_chapters_view(request):
    profile = request.user.profile

    if profile.status == 'gm':
        chapters = Chapter.objects.prefetch_related(
            'game_sessions__chronicle_events__informed',
            'game_sessions__chronicle_events__pictures',
            'game_sessions__chronicle_events__notes__author',
            'game_sessions__chronicle_events__debate__topic'
        )
    else:
        events = (profile.chronicle_events_participated.all()
                  | profile.chronicle_events_informed.all())\
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

    if profile.status == 'gm':
        games = chapter.game_sessions.prefetch_related(
            'chronicle_events__informed',
            'chronicle_events__pictures',
            'chronicle_events__notes__author',
            'chronicle_events__debate__topic'
            )
    else:
        events = (profile.chronicle_events_participated.all()
                  | profile.chronicle_events_informed.all())\
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

    if profile.status == 'gm':
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
        return redirect('history:chronicle-gap',
                        timeline_event_id=timeline_event_id)
    else:
        return redirect('home:dupa')


@query_debugger
@login_required
def chronicle_inform_view(request, event_id):
    profile = request.user.profile
    chronicle_event = get_object_or_404(ChronicleEvent, id=event_id)

    participants = chronicle_event.participants.all()
    informed = chronicle_event.informed.all()
    allowed = (participants | informed)

    # INFORM FORM
    # dict(request.POST).items() == < QueryDict: {
    #     'csrfmiddlewaretoken': ['KcoYDwb7r86Ll2SdQUNrDCKs...'],
    #     '2': ['on'],
    #     'chronicle_event': ['122']
    # } >
    if request.method == 'POST' and 'chronicle_event' in request.POST:
        data = dict(request.POST)
        informed_ids = [k for k, v_list in data.items() if 'on' in v_list]
        chronicle_event.informed.add(*informed_ids)
    
        send_emails(request, informed_ids, chronicle_event=chronicle_event)
        if informed_ids:
            messages.info(request, f'Poinformowano wybrane postacie!')

    context = {
        'page_title': 'Poinformuj o wydarzeniu',
        'event': chronicle_event,
        'event_type': 'chronicle_event'
    }

    # if is_allowed_for_chronicle(profile, chronicle_event_id=event_id):
    if profile in allowed or profile.status == 'gm':
        return render(request, 'history/_event_inform.html', context)
    else:
        return redirect('home:dupa')


@query_debugger
@login_required
def chronicle_note_view(request, event_id):
    profile = request.user.profile
    event = get_object_or_404(ChronicleEvent, id=event_id)
    current_note = None

    try:
        current_note = ChronicleEventNote.objects.get(event=event,
                                                      author=request.user)
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
    if profile.status == 'gm':
        return render(request, 'history/chronicle_edit.html', context)
    else:
        return redirect('home:dupa')


@query_debugger
@login_required
def chronicle_gap_view(request, timeline_event_id):
    timeline_event = get_object_or_404(TimelineEvent, id=timeline_event_id)
    participants_and_informed = (timeline_event.participants.all()
                                 | (timeline_event.informed.all())).distinct()
    participants_and_informed_str = ', '.join(p.character_name.split(' ', 1)[0]
                                              for p in participants_and_informed)

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

    if profile.status == 'gm':
        threads = Thread.objects.all()
        participants = Profile.objects.filter(status__in=['active_player', 'inactive_player', 'dead_player'])
        spec_locs = SpecificLocation.objects.annotate(events_cnt=Count('timeline_events')).filter(events_cnt__gt=0)
        gen_locs = GeneralLocation.objects\
            .annotate(events_cnt=Count('timeline_events'))\
            .filter(events_cnt__gt=0)\
            .prefetch_related(Prefetch('specific_locations', queryset=spec_locs))
        games = GameSession.objects.annotate(num_events=Count('timeline_events')).filter(num_events__gt=0)
        events = TimelineEvent.objects.all()
    else:
        threads = Thread.objects\
            .filter(Q(timeline_events__participants=profile) | Q(timeline_events__informed=profile))\
            .distinct()
        participants = Profile.objects\
            .filter(status__in=['active_player', 'inactive_player', 'dead_player'])\
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
def timeline_filter_events_view(request, thread_id=0, participant_id=0, gen_loc_id=0, spec_loc_id=0,
                                year=0, season='0', game_id=0):
    profile = request.user.profile

    if thread_id != 0:
        thread = get_object_or_404(Thread, id=thread_id)
        page_title = thread.name
        header = f'{thread.name}... Próbujesz sobie przypomnieć, od czego się to wszystko zaczęło?'

        if profile.status == 'gm':
            events = TimelineEvent.objects.filter(threads=thread)
        else:
            events = (profile.timeline_events_participated.all() | profile.timeline_events_informed.all()) \
                .filter(threads=thread) \
                .distinct()

    elif participant_id != 0:
        participant = get_object_or_404(Profile, id=participant_id)
        page_title = participant.character_name
        if profile == participant:
            header = 'Są czasy, gdy ogarnia Cię zaduma nad Twoim zawikłanym losem...'
        else:
            header = f'{participant.character_name.split(" ", 1)[0]}... ' \
                     f'Niejedno razem przeżyliście. Na dobre i na złe...'

        if profile.status == 'gm':
            events = TimelineEvent.objects.filter(participants=participant_id)
        else:
            events = (profile.timeline_events_participated.all() | profile.timeline_events_informed.all()) \
                .filter(participants=participant_id) \
                .distinct()

    elif gen_loc_id != 0:
        general_location = get_object_or_404(GeneralLocation, id=gen_loc_id)
        page_title = general_location.name
        header = f'{general_location.name}... Zastanawiasz się, jakie piętno wywarła na Twoich losach ta kraina...'

        if profile.status == 'gm':
            events = TimelineEvent.objects.filter(general_locations=gen_loc_id)
        else:
            events = (profile.timeline_events_participated.all() | profile.timeline_events_informed.all()) \
                .filter(general_locations=gen_loc_id) \
                .distinct()

    elif spec_loc_id != 0:
        specific_location = get_object_or_404(SpecificLocation, id=spec_loc_id)
        page_title = specific_location.name
        header = f'{specific_location.name}... Jak to miejsce odcisnęło się na Twoim losie?'

        if profile.status == 'gm':
            events = TimelineEvent.objects.filter(specific_locations=spec_loc_id)
        else:
            events = (profile.timeline_events_participated.all() | profile.timeline_events_informed.all()) \
                .filter(specific_locations=spec_loc_id) \
                .distinct()

    elif game_id != 0:
        game = get_object_or_404(GameSession, id=game_id)
        page_title = game.title
        header = f'{game.title}... Jak to po kolei było?'

        if profile.status == 'gm':
            events = TimelineEvent.objects.filter(game=game_id)
        else:
            events = (profile.timeline_events_participated.all() | profile.timeline_events_informed.all())\
                .filter(game=game_id)\
                .distinct()

    elif year:
        page_title = ''
        header = f'Nie wydaje się to wcale aż tak dawno temu...'

        if profile.status == 'gm':
            events = TimelineEvent.objects.all()
        else:
            events = (profile.timeline_events_participated.all() | profile.timeline_events_informed.all()) \
                .distinct()

        if year and season == '0':
            events = events.filter(year=year)
            page_title = f'{year}. rok Archonatu Nemetha Samatiana'
        elif year:
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

    else:
        page_title = 'Pełne Kalendarium'
        header = 'Opisane tu wydarzenia rozpoczęły swój bieg 20. roku Archonatu Nemetha Samatiana w Ebbonie, ' \
                 'choć zarodki wielu z nich sięgają znacznie odleglejszych czasów...'

        if profile.status == 'gm':
            events = TimelineEvent.objects.all()
        else:
            events = (profile.timeline_events_participated.all() | profile.timeline_events_informed.all()) \
                .distinct()

    events = events\
        .select_related('game')\
        .prefetch_related('threads', 'participants', 'informed', 'general_locations',
                          'specific_locations__general_location', 'notes__author')

    context = {
        'page_title': page_title,
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
def timeline_inform_view(request, event_id):
    profile = request.user.profile
    timeline_event = get_object_or_404(TimelineEvent, id=event_id)

    participants = timeline_event.participants.all()
    informed = timeline_event.informed.all()
    allowed = (participants | informed)

    # INFORM FORM
    # dict(request.POST).items() == < QueryDict: {
    #     'csrfmiddlewaretoken': ['KcoYDwb7r86Ll2SdQUNrDCKs...'],
    #     '2': ['on'],
    #     'timeline_event': ['122']
    # } >
    if request.method == 'POST' and 'timeline_event' in request.POST:
        data = dict(request.POST)
        informed_ids = [k for k, v_list in data.items() if 'on' in v_list]
        timeline_event.informed.add(*informed_ids)
    
        send_emails(request, informed_ids, timeline_event=timeline_event)
        if informed_ids:
            messages.info(request, f'Poinformowano wybrane postacie!')

    context = {
        'page_title': 'Poinformuj o wydarzeniu',
        'event': timeline_event,
        'event_type': 'timeline_event'
    }
    if profile in allowed or profile.status == 'gm':
        return render(request, 'history/_event_inform.html', context)
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
    if profile in (event.participants.all() | event.informed.all()) or profile.status == 'gm':
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
    if profile.status == 'gm':
        return render(request, 'history/timeline_edit.html', context)
    else:
        return redirect('home:dupa')

