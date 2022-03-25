from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch, Q, Count
from django.shortcuts import render, redirect, get_object_or_404

from chronicles.filters import GameEventFilter
from chronicles.models import (
    Chapter,
    GameSession,
    GameEvent,
    TimeUnit,
    Chronology,
)
from rpg_project.utils import send_emails
from toponomikon.models import Location
from users.models import Profile


# #################### CHRONICLE ####################


@login_required
def chronicle_main_view(request):
    current_profile = Profile.objects.get(id=request.session['profile_id'])
    
    if current_profile.can_view_all:
        games = GameSession.objects.prefetch_related(
            'game_events__participants__character',
            'game_events__debates__participants__character',
        )
    else:
        debates = current_profile.threads_participated.filter(kind='Debate')
        debates = debates.prefetch_related('participants__character')
        
        events = GameEvent.objects.filter(
            Q(id__in=current_profile.events_participated.all())
            | Q(id__in=current_profile.events_informed.all()))
        events = events.prefetch_related(
            Prefetch('debates', queryset=debates),
            'participants__character')
        
        games = GameSession.objects.filter(game_events__in=events)
        games = games.prefetch_related(Prefetch('game_events', queryset=events))
        games = games.annotate(
            any_participants=Count(
                'game_events',
                filter=Q(game_events__in=current_profile.events_participated.all())))
           
    games = games.order_by('game_no').select_related('chapter').exclude(game_no=0)
    chapters = Chapter.objects.filter(game_sessions__in=games).distinct()

    context = {
        'current_profile': current_profile,
        'page_title': 'Kronika',
        'chapters': chapters,
        'games': games,
    }
    return render(request, 'chronicles/chronicle_main.html', context)


@login_required
def chronicle_game_view(request, game_id):
    current_profile = Profile.objects.get(id=request.session['profile_id'])
    
    game = get_object_or_404(GameSession, id=game_id)
    events = GameEvent.objects.filter(game=game)
    events = events.prefetch_related(
        'participants',
        'informees',
        'picture_sets',
        'debates__statements__author',
        'debates__statements__seen_by',
        'debates__participants',
    )
    if not current_profile.can_view_all:
        events = events.filter(
            Q(participants=current_profile) | Q(informees=current_profile))
        events = events.distinct()

    context = {
        'current_profile': current_profile,
        'page_title': game.title,
        'events': events,
    }
    if events:
        return render(request, 'chronicles/chronicle_game.html', context)
    else:
        return redirect('users:dupa')


@login_required
def chronicle_chapter_view(request, chapter_id):
    current_profile = Profile.objects.get(id=request.session['profile_id'])
    chapter = get_object_or_404(Chapter, id=chapter_id)
    events = GameEvent.objects.filter(game__chapter=chapter)
    events = events.prefetch_related(
        'participants',
        'informees',
        'picture_sets',
        'debates__statements__author',
        'debates__statements__seen_by',
        'debates__participants',
    )
    if not current_profile.can_view_all:
        events = events.filter(
            Q(participants=current_profile) | Q(informees=current_profile))
        events = events.distinct()
        
    games = GameSession.objects.filter(game_events__in=events)
    games = games.prefetch_related(Prefetch('game_events', queryset=events))
    games = games.distinct()

    context = {
        'current_profile': current_profile,
        'page_title': chapter.title,
        'games': games,
    }
    if games:
        return render(request, 'chronicles/chronicle_chapter.html', context)
    else:
        return redirect('users:dupa')


@login_required
def chronicle_all_view(request):
    current_profile = Profile.objects.get(id=request.session['profile_id'])
    events = GameEvent.objects.prefetch_related(
        'participants',
        'informees',
        'picture_sets',
        'debates__statements__author',
        # 'debates__statements__seen_by',   # TODO add in Postgres, now causes SQLite error "Too many SQl variables"
        'debates__participants',
    )
    if not current_profile.can_view_all:
        events = events.filter(
            Q(participants=current_profile) | Q(informees=current_profile))
        events = events.distinct()
    
    games = GameSession.objects.filter(game_events__in=events)
    games = games.prefetch_related(Prefetch('game_events', queryset=events))
    games = games.distinct()
    
    chapters = Chapter.objects.filter(game_sessions__in=games)
    chapters = chapters.prefetch_related(
        Prefetch('game_sessions', queryset=games)
    )
    chapters = chapters.distinct()
    
    context = {
        'current_profile': current_profile,
        'page_title': 'Pełna kronika',
        'chapters': chapters,
    }
    if chapters:
        return render(request, 'chronicles/chronicle_all.html', context)
    else:
        return redirect('users:dupa')
    

#  TODO another view for HistoryEvent ?
#  TODO or maybe just check if id in GameEvent or HistoryEvent
@login_required
def game_event_inform_view(request, game_event_id):
    current_profile = Profile.objects.get(id=request.session['profile_id'])
    game_event = get_object_or_404(TimeUnit, id=game_event_id)
    allowed = (
        game_event.participants.all() | game_event.informees.all()
    )
    allowed = allowed.filter(status='player')
    
    # INFORM FORM
    # dict(request.POST).items() == < QueryDict: {
    #     'csrfmiddlewaretoken': ['KcoYDwb7r86Ll2SdQUNrDCKs...'],
    #     '2': ['on'],
    #     'chronicle_event': ['122']
    # } >
    if request.method == 'POST' and 'game_event' in request.POST:
        data = dict(request.POST)
        informed_ids = [k for k, v_list in data.items() if 'on' in v_list]
        game_event.informees.add(*informed_ids)

        send_emails(request, informed_ids, game_event=game_event)
        if informed_ids:
            messages.info(request, f'Poinformowano wybrane Postacie!')

    context = {
        'current_profile': current_profile,
        'page_title': 'Poinformuj o wydarzeniu',
        'event': game_event,
        'event_type': 'game_event'
    }
    if current_profile in allowed or current_profile.status == 'gm':
        return render(request, 'chronicles/_event_inform.html', context)
    else:
        return redirect('users:dupa')


def chronologies_view(request):
    current_profile = Profile.objects.get(id=request.session['profile_id'])
    
    chronologies = Chronology.objects.prefetch_related(
        'timeunits__timeunits__timeunits',
        'timeunits__date_start',
        'timeunits__date_end',
        'timeunits__timeunits__date_start',
        'timeunits__timeunits__date_end',
        'timeunits__timeunits__timeunits__date_start',
        'timeunits__timeunits__timeunits__date_end',
        
    ).select_related('in_timeunit')
    
    context = {
        'current_profile': current_profile,
        'page_title': 'Chronologie',
        'chronologies': chronologies,
        'event_type': 'game_event'
    }
    return render(request, 'chronicles/chronologies.html', context)


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# --------------------------------- TIMELINE ----------------------------------
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------


@login_required
def timeline_view(request):
    current_profile = Profile.objects.get(id=request.session['profile_id'])

    events = GameEvent.objects.all()
    if not current_profile.can_view_all:
        events = events.filter(
            Q(id__in=current_profile.events_participated.all())
            | Q(id__in=current_profile.events_informed.all())
        )
        events = events.distinct()
        
    events = events.prefetch_related(
        'plot_threads',
        'participants__user',
        'informees__user',
        'participants__character',
        'informees__character',
        'locations',
    )
    events = events.order_by(
        # DON'T ORDER BY 'game': this would mix events from 2+ synchronic games
        'in_timeunit__in_timeunit__in_timeunit__date_start__year',
        'in_timeunit__in_timeunit__date_start__year',
        'in_timeunit__date_start__year',
        'date_start__year',
        'date_start__season',
        'date_start__day',
        
        # Ordering by these might be problematic for HistoryEvents,
        # but is necessary to properly order events from to 2+ synchronic games
        'game',     # No -game: later game's events are usually later
        'event_no_in_game',
    )
    
    # Modify locations filter to include sublocations
    request = add_sublocations(request)
    events_filter = GameEventFilter(
        request.GET, queryset=events, request=request)
   
    context = {
        'current_profile': current_profile,
        'page_title': 'Pełne Kalendarium',
       
        # TODO the use of filter rises query cnt from 8 to 13, somehow causing
        #  2x queries for certain fields. Try to resolve it in the future.
        'events_filter': events_filter,
    }
    return render(request, 'chronicles/timeline.html', context)


def add_sublocations(request):
    all_locs_ids = []
    for loc_id in request.GET.getlist('locations'):
        sublocations = Location.objects.get(id=loc_id).with_sublocations()
        all_locs_ids.extend([s.id for s in sublocations])
        
    request.GET = request.GET.copy()
    request.GET.setlist('locations', all_locs_ids)
    return request
