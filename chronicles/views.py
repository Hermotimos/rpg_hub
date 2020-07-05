from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch, Q, When, Case, Value, IntegerField, Count
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404

# from history.models import (TimelineEvent, ChronicleEvent, Chapter,
#                             GameSession, Thread)
from chronicles.models import (Chapter, GameSession, Thread, Date, GameEvent, TimeUnit)
from rpg_project.utils import send_emails
from toponomikon.models import Location
from users.models import Profile


# #################### CHRONICLE ####################


@login_required
def chronicle_contents_view(request):
    profile = request.user.profile
    
    if profile.status == 'gm':
        chapters = Chapter.objects.prefetch_related('game_sessions')
    else:
        events = GameEvent.objects.filter(
            Q(id__in=profile.events_known_directly.all())
            | Q(id__in=profile.events_known_indirectly.all())
        )
        events_known_directly = GameEvent.objects.filter(
            id__in=profile.events_known_directly.all()
        )
        
        games = GameSession.objects.filter(events__in=events)
        games = games.prefetch_related(Prefetch('events', queryset=events))
        games = games.annotate(
            any_known_directly=Count(
                'events',
                filter=Q(events__in=events_known_directly)
            )
        )
        games = games.distinct()
        
        chapters = Chapter.objects.filter(game_sessions__in=games)
        chapters = chapters.prefetch_related(
            Prefetch('game_sessions', queryset=games)
        )
        chapters = chapters.distinct()
        
    context = {
        'page_title': 'Kronika',
        'chapters': chapters,
    }
    return render(request, 'chronicles/chronicle_contents.html', context)


@login_required
def chronicle_game_view(request, game_id):
    profile = request.user.profile
    game = get_object_or_404(GameSession, id=game_id)
    
    events = GameEvent.objects.filter(game=game)
    events = events.prefetch_related(
        'known_directly',
        'known_indirectly',
        'pictures',
    )
    events = events.select_related('debate__topic')
    if not profile.status == 'gm':
        events = events.filter(
            Q(known_directly=profile) | Q(known_indirectly=profile)
        )
        events = events.distinct()

    context = {
        'page_title': game.title,
        'events': events,
    }
    if events:
        return render(request, 'chronicles/chronicle_game.html', context)
    else:
        return redirect('home:dupa')


@login_required
def chronicle_chapter_view(request, chapter_id):
    profile = request.user.profile
    chapter = get_object_or_404(Chapter, id=chapter_id)

    events = GameEvent.objects.filter(game__chapter=chapter)
    events = events.prefetch_related(
        'known_directly',
        'known_indirectly',
        'pictures',
    )
    events = events.select_related('debate__topic')
    if not profile.status == 'gm':
        events = events.filter(
            Q(known_directly=profile) | Q(known_indirectly=profile)
        )
        events = events.distinct()
        
    games = GameSession.objects.filter(events__in=events)
    games = games.prefetch_related(Prefetch('events', queryset=events))
    games = games.distinct()
    
    context = {
        'page_title': chapter.title,
        'games': games,
    }
    if games:
        return render(request, 'chronicles/chronicle_chapter.html', context)
    else:
        return redirect('home:dupa')


@login_required
def chronicle_all_view(request):
    profile = request.user.profile
    
    events = GameEvent.objects.prefetch_related(
        'known_directly',
        'known_indirectly',
        'pictures',
    )
    events = events.select_related('debate__topic')
    if not profile.status == 'gm':
        events = events.filter(
            Q(known_directly=profile) | Q(known_indirectly=profile)
        )
        events = events.distinct()
    
    games = GameSession.objects.filter(events__in=events)
    games = games.prefetch_related(Prefetch('events', queryset=events))
    games = games.distinct()
    
    chapters = Chapter.objects.filter(game_sessions__in=games)
    chapters = chapters.prefetch_related(
        Prefetch('game_sessions', queryset=games)
    )
    chapters = chapters.distinct()
    
    context = {
        'page_title': 'Pełna kronika',
        'chapters': chapters,
    }
    if chapters:
        return render(request, 'chronicles/chronicle_all.html', context)
    else:
        return redirect('home:dupa')
    

#  TODO another view for HistoryEvent ?
#  TODO or maybe just check if id in GameEvent or HistoryEvent
@login_required
def game_event_inform_view(request, game_event_id):
    profile = request.user.profile
    game_event = get_object_or_404(TimeUnit, id=game_event_id)
    allowed = (
        game_event.known_directly.all() | game_event.known_indirectly.all()
    )
    allowed = allowed.filter(status__in=['active_player', 'inactive_player'])
    
    # INFORM FORM
    # dict(request.POST).items() == < QueryDict: {
    #     'csrfmiddlewaretoken': ['KcoYDwb7r86Ll2SdQUNrDCKs...'],
    #     '2': ['on'],
    #     'chronicle_event': ['122']
    # } >
    if request.method == 'POST' and 'game_event' in request.POST:
        data = dict(request.POST)
        informed_ids = [k for k, v_list in data.items() if 'on' in v_list]
        game_event.known_indirectly.add(*informed_ids)

        send_emails(request, informed_ids, game_event=game_event)
        if informed_ids:
            messages.info(request, f'Poinformowano wybrane postacie!')

    context = {
        'page_title': 'Poinformuj o wydarzeniu',
        'event': game_event,
        'event_type': 'game_event'
    }
    if profile in allowed or profile.status == 'gm':
        return render(request, 'chronicles/_event_inform.html', context)
    else:
        return redirect('home:dupa')












#
# # #################### TIMELINE: model TimelineEvent ####################


SEASONS_WITH_STYLES_DICT = {
    '1': 'season-spring',
    '2': 'season-summer',
    '3': 'season-autumn',
    '4': 'season-winter'
}


# @login_required
# def timeline_main_view(request):
#     profile = request.user.profile
#
#     if profile.status == 'gm':
#         threads = Thread.objects.all()
#         participants = Profile.objects\
#             .filter(status__in=['active_player', 'inactive_player', 'dead_player'])
#         locs_lvl_2 = Location.objects\
#             .filter(~Q(in_location=None))\
#             .annotate(events_cnt=Count('timeline_events_in_spec'))\
#             .filter(events_cnt__gt=0)
#         locs_lvl_1 = Location.objects\
#             .filter(in_location=None)\
#             .annotate(events_cnt=Count('timeline_events_in_gen'))\
#             .filter(events_cnt__gt=0)\
#             .prefetch_related(Prefetch('locations', queryset=locs_lvl_2))
#         games = GameSession.objects\
#             .annotate(num_events=Count('timeline_events'))\
#             .filter(num_events__gt=0)
#         events = TimelineEvent.objects.all()
#     else:
#         threads = Thread.objects\
#             .filter(Q(timeline_events__participants=profile) | Q(timeline_events__informed=profile))\
#             .distinct()
#         participants = Profile.objects\
#             .filter(status__in=['active_player', 'inactive_player', 'dead_player'])\
#             .filter(timeline_events_participated__in=profile.timeline_events_participated.all())\
#             .distinct()
#         locs_lvl_2 = Location.objects\
#             .filter(~Q(in_location=None)) \
#             .filter(Q(timeline_events_in_spec__participants=profile) | Q(timeline_events_in_spec__informed=profile)) \
#             .distinct()
#         locs_lvl_1 = Location.objects\
#             .filter(in_location=None)\
#             .filter(locations__in=locs_lvl_2)\
#             .distinct()\
#             .prefetch_related(Prefetch('locations', queryset=locs_lvl_2))
#         games = GameSession.objects \
#             .filter(Q(timeline_events__participants=profile) | Q(timeline_events__informed=profile)) \
#             .distinct()
#         events = (profile.timeline_events_participated.all() | profile.timeline_events_informed.all())\
#             .distinct()
#
#     years = list({y for y in (e.year for e in events)})
#     years.sort()
#     years_with_seasons_dict = {}
#     for y in years:
#         seasons = list({e.season for e in events if e.year == y})
#         seasons.sort()
#         years_with_seasons_dict[y] = seasons
#
#     context = {
#         'page_title': 'Kalendarium',
#         'seasons_with_styles_dict': SEASONS_WITH_STYLES_DICT,
#         'years_with_seasons_dict': years_with_seasons_dict,
#         'threads': threads,
#         'participants': participants,
#         'gen_locs': locs_lvl_1,
#         'games': games,
#     }
#     return render(request, 'history/timeline_main.html', context)
#

@login_required
def timeline_view(request):
    profile = request.user.profile

    page_title = 'Pełne Kalendarium'
    header = 'Opisane tu wydarzenia rozpoczęły swój bieg 20. roku Archonatu Nemetha Samatiana w Ebbonie, ' \
             'choć zarodki wielu z nich sięgają znacznie odleglejszych czasów...'
    
    events = GameEvent.objects.select_related('game')
    events = events.prefetch_related(
        'threads',
        'known_directly',
        'known_indirectly',
        'primary_locations',
        'secondary_locations__in_location',
    )
    if not profile.status == 'gm':
        events = GameEvent.objects.filter(
            Q(id__in=profile.events_known_directly.all())
            | Q(id__in=profile.events_known_indirectly.all())
        )
    events = events.distinct()

    context = {
        'page_title': page_title,
        'header': header,
        'events': events,
        'seasons_with_styles_dict': SEASONS_WITH_STYLES_DICT,
    }
    if events:
        return render(request, 'chronicles/timeline.html', context)
    else:
        return redirect('home:dupa')


# @login_required
# def timeline_inform_view(request, event_id):
#     profile = request.user.profile
#     timeline_event = get_object_or_404(TimelineEvent, id=event_id)
#
#     participants = timeline_event.participants.all()
#     informed = timeline_event.informed.all()
#     allowed = (participants | informed)
#
#     # INFORM FORM
#     # dict(request.POST).items() == < QueryDict: {
#     #     'csrfmiddlewaretoken': ['KcoYDwb7r86Ll2SdQUNrDCKs...'],
#     #     '2': ['on'],
#     #     'timeline_event': ['122']
#     # } >
#     if request.method == 'POST' and 'timeline_event' in request.POST:
#         data = dict(request.POST)
#         informed_ids = [k for k, v_list in data.items() if 'on' in v_list]
#         timeline_event.informed.add(*informed_ids)
#
#         send_emails(request, informed_ids, timeline_event=timeline_event)
#         if informed_ids:
#             messages.info(request, f'Poinformowano wybrane postacie!')
#
#     context = {
#         'page_title': 'Poinformuj o wydarzeniu',
#         'event': timeline_event,
#         'event_type': 'timeline_event'
#     }
#     if profile in allowed or profile.status == 'gm':
#         return render(request, 'history/_event_inform.html', context)
#     else:
#         return redirect('home:dupa')
