from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch, Q, When, Case, Value, IntegerField, Count
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404

# from history.models import (TimelineEvent, ChronicleEvent, Chapter,
#                             GameSession, Thread)
from chronicles.models import (Chapter, GameSession, Thread, Date, GameEvent)
from rpg_project.utils import send_emails
from toponomikon.models import Location
from users.models import Profile


# #################### CHRONICLE: model ChronicleEvent ####################


# def is_allowed_for_chronicle(profile, chapter_id=0, game_id=0,
#                              chronicle_event_id=0, timeline_event_id=0):
#
#     if profile.status == 'gm':
#         return True
#     elif chapter_id:
#         if chapter_id in [ch.id for ch in Chapter.objects.filter(
#                 Q(game_sessions__chronicle_events__participants=profile)
#                 | Q(game_sessions__chronicle_events__informed=profile))]:
#             return True
#     elif game_id:
#         if game_id in [g.id for g in GameSession.objects.filter(
#                 Q(chronicle_events__participants=profile)
#                 | Q(chronicle_events__informed=profile))]:
#             return True
#     elif chronicle_event_id:
#         if chronicle_event_id in [e.id for e in GameEvent.objects.filter(
#                 Q(participants=profile) | Q(informed=profile))]:
#             return True
#     elif timeline_event_id:
#         if timeline_event_id in [e.id for e in TimelineEvent.objects.filter(
#                 Q(participants=profile) | Q(informed=profile))]:
#             return True
#     else:
#         return False


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
def chronicle_game_view(request, game_title):
    profile = request.user.profile
    game = get_object_or_404(GameSession, title=game_title)
    
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
        'page_title': game_title,
        'events': events,
    }
    if events:
        return render(request, 'chronicles/chronicle_game.html', context)
    else:
        return redirect('home:dupa')


@login_required
def chronicle_chapter_view(request, chapter_title):
    profile = request.user.profile
    chapter = get_object_or_404(Chapter, title=chapter_title)

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
        
    games = GameSession.objects.filter(chapter=chapter)
    games = GameSession.objects.filter(events__in=events)
    games = games.prefetch_related(Prefetch('events', queryset=events))
    games = games.distinct()
    
    context = {
        'page_title': chapter_title,
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
    








#
#
# @login_required
# def chronicle_inform_view(request, event_id):
#     profile = request.user.profile
#     chronicle_event = get_object_or_404(ChronicleEvent, id=event_id)
#
#     participants = chronicle_event.participants.all()
#     informed = chronicle_event.informed.all()
#     allowed = (participants | informed)
#
#     # INFORM FORM
#     # dict(request.POST).items() == < QueryDict: {
#     #     'csrfmiddlewaretoken': ['KcoYDwb7r86Ll2SdQUNrDCKs...'],
#     #     '2': ['on'],
#     #     'chronicle_event': ['122']
#     # } >
#     if request.method == 'POST' and 'chronicle_event' in request.POST:
#         data = dict(request.POST)
#         informed_ids = [k for k, v_list in data.items() if 'on' in v_list]
#         chronicle_event.informed.add(*informed_ids)
#
#         send_emails(request, informed_ids, chronicle_event=chronicle_event)
#         if informed_ids:
#             messages.info(request, f'Poinformowano wybrane postacie!')
#
#     context = {
#         'page_title': 'Poinformuj o wydarzeniu',
#         'event': chronicle_event,
#         'event_type': 'chronicle_event'
#     }
#
#     # if is_allowed_for_chronicle(profile, chronicle_event_id=event_id):
#     if profile in allowed or profile.status == 'gm':
#         return render(request, 'history/_event_inform.html', context)
#     else:
#         return redirect('home:dupa')
#
#
# @login_required
# def chronicle_gap_view(request, timeline_event_id):
#     timeline_event = get_object_or_404(TimelineEvent, id=timeline_event_id)
#     participants_and_informed = (timeline_event.participants.all()
#                                  | (timeline_event.informed.all())).distinct()
#     participants_and_informed_str = ', '.join(p.character_name.split(' ', 1)[0]
#                                               for p in participants_and_informed)
#
#     context = {
#         'page_title': 'Luka w Kronice',
#         'participants_and_informed': participants_and_informed_str
#     }
#     return render(request, 'history/chronicle_gap.html', context)
#
#
# # #################### TIMELINE: model TimelineEvent ####################
#
#
# SEASONS_WITH_STYLES_DICT = {
#     '1': 'season-spring',
#     '2': 'season-summer',
#     '3': 'season-autumn',
#     '4': 'season-winter'
# }
#
#
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
#
# @login_required
# def timeline_filter_events_view(request, thread_id=0, participant_id=0, gen_loc_id=0, spec_loc_id=0,
#                                 year=0, season='0', game_id=0):
#     profile = request.user.profile
#
#     if thread_id != 0:
#         thread = get_object_or_404(Thread, id=thread_id)
#         page_title = thread.name
#         header = f'{thread.name}... Próbujesz sobie przypomnieć, od czego się to wszystko zaczęło?'
#
#         if profile.status == 'gm':
#             events = TimelineEvent.objects.filter(threads=thread)
#         else:
#             events = (profile.timeline_events_participated.all() | profile.timeline_events_informed.all()) \
#                 .filter(threads=thread) \
#                 .distinct()
#
#     elif participant_id != 0:
#         participant = get_object_or_404(Profile, id=participant_id)
#         page_title = participant.character_name
#         if profile == participant:
#             header = 'Są czasy, gdy ogarnia Cię zaduma nad Twoim zawikłanym losem...'
#         else:
#             header = f'{participant.character_name.split(" ", 1)[0]}... ' \
#                      f'Niejedno razem przeżyliście. Na dobre i na złe...'
#
#         if profile.status == 'gm':
#             events = TimelineEvent.objects.filter(participants=participant_id)
#         else:
#             events = (profile.timeline_events_participated.all() | profile.timeline_events_informed.all()) \
#                 .filter(participants=participant_id) \
#                 .distinct()
#
#     elif gen_loc_id != 0:
#         gen_location = get_object_or_404(Location, id=gen_loc_id)
#         page_title = gen_location.name
#         header = f'{gen_location.name}... Zastanawiasz się, jakie piętno wywarła na Twoich losach ta kraina...'
#
#         if profile.status == 'gm':
#             events = TimelineEvent.objects.filter(gen_locations=gen_loc_id)
#         else:
#             events = (profile.timeline_events_participated.all() | profile.timeline_events_informed.all()) \
#                 .filter(gen_locations=gen_loc_id) \
#                 .distinct()
#
#     elif spec_loc_id != 0:
#         spec_location = get_object_or_404(Location, id=spec_loc_id)
#         page_title = spec_location.name
#         header = f'{spec_location.name}... Jak to miejsce odcisnęło się na Twoim losie?'
#
#         if profile.status == 'gm':
#             events = TimelineEvent.objects.filter(spec_locations=spec_loc_id)
#         else:
#             events = (profile.timeline_events_participated.all() | profile.timeline_events_informed.all()) \
#                 .filter(spec_locations=spec_loc_id) \
#                 .distinct()
#
#     elif game_id != 0:
#         game = get_object_or_404(GameSession, id=game_id)
#         page_title = game.title
#         header = f'{game.title}... Jak to po kolei było?'
#
#         if profile.status == 'gm':
#             events = TimelineEvent.objects.filter(game=game_id)
#         else:
#             events = (profile.timeline_events_participated.all() | profile.timeline_events_informed.all())\
#                 .filter(game=game_id)\
#                 .distinct()
#
#     elif year:
#         page_title = ''
#         header = f'Nie wydaje się to wcale aż tak dawno temu...'
#
#         if profile.status == 'gm':
#             events = TimelineEvent.objects.all()
#         else:
#             events = (profile.timeline_events_participated.all() | profile.timeline_events_informed.all()) \
#                 .distinct()
#
#         if year and season == '0':
#             events = events.filter(year=year)
#             page_title = f'{year}. rok Archonatu Nemetha Samatiana'
#         elif year:
#             if season == '1':
#                 season_name = 'Wiosna'
#             elif season == '2':
#                 season_name = "Lato"
#             elif season == '3':
#                 season_name = "Jesień"
#             else:
#                 season_name = "Zima"
#             events = events.filter(year=year, season=season)
#             page_title = f'{season_name} {year}. roku Archonatu Nemetha Samatiana'
#
#     else:
#         page_title = 'Pełne Kalendarium'
#         header = 'Opisane tu wydarzenia rozpoczęły swój bieg 20. roku Archonatu Nemetha Samatiana w Ebbonie, ' \
#                  'choć zarodki wielu z nich sięgają znacznie odleglejszych czasów...'
#
#         if profile.status == 'gm':
#             events = TimelineEvent.objects.all()
#         else:
#             events = (profile.timeline_events_participated.all() | profile.timeline_events_informed.all()) \
#                 .distinct()
#
#     events = events\
#         .select_related('game')\
#         .prefetch_related('threads', 'participants', 'informed', 'gen_locations',
#                           'spec_locations__in_location',
#                           # 'notes__author'
#                           )
#
#     context = {
#         'page_title': page_title,
#         'header': header,
#         'events': events,
#         'seasons_with_styles_dict': SEASONS_WITH_STYLES_DICT,
#     }
#     if events:
#         return render(request, 'history/timeline_events.html', context)
#     else:
#         return redirect('home:dupa')
#
#
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
