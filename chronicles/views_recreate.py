from django.db.models import Q

from debates.models import Debate
from imaginarion.models import Picture
from django.shortcuts import render, redirect, get_object_or_404

from toponomikon.models import PrimaryLocation, SecondaryLocation
from users.models import Profile
from chronicles.models import Thread, Date, TimeUnit, Chronology, \
    Era, Period, GameEvent, Chapter, GameSession, GameEvent


from history.models import (
    GameSession as GameSession_H,
    Thread as Thread_H,
    Chapter as Chapter_H,
    ChronicleEvent as ChronicleEvent_H
)


def recreate(request):

    for chapter in Chapter_H.objects.all():
        try:
            Chapter.objects.create(
                chapter_no=chapter.chapter_no,
                title=chapter.title,
                image=None,
            )
        except Exception as exc:
            print(f'Failed creating from: {Chapter_H.__name__}: {chapter.title}\n{exc}')

    for thread in Thread_H.objects.all():
        try:
            Thread.objects.create(
                name=thread.name,
                is_ended=thread.is_ended,
                sorting_name=thread.sorting_name,
            )
        except Exception as exc:
            print(f'Failed creating from: {Thread_H.__name__}: {thread.name}\n{exc}')

    for game in GameSession_H.objects.all():
        try:
            GameSession.objects.create(
                game_no=game.game_no,
                title=game.title,
                chapter=Chapter.objects.get(title=game.chapter.title) or None,
                date=game.date,
            )
        except Exception as exc:
            print(f'Failed creating from: {GameSession_H.__name__}: {game.title}\n{exc}')
            
    # TODO - chapter.image - gotta do it manually
    # TODO - GameSession with no 0 fails - 'Wydarzenia na świecie' - add manually
    
    
    # Create CHRONOLOGIA
    e_chrono = Chronology.objects.create(
        name='Chronologia Traegharon i Hyllemath',
        name_genetive='Chronologii Traegharon i Hyllemath',
        description_short=None,
        description_long=None,
        in_timeunit=None,
        date_start=Date.objects.create(day=None, season=None, year=1),
        date_end=None,
    )
    e_chrono.known_directly.set(*[Profile.objects.filter(status=Q(status='active_player') | Q(status='inactive_player') | Q(status='dead_player'))])
    e_chrono.primary_locations.add(PrimaryLocation.objects.get(name='Hyllemath'))
    e_chrono.save()

    # Create ERA
    e_era = Era.objects.create(
        name='Nowa Era',
        name_genetive='Nowej Ery',
        description_short=None,
        description_long=None,
        in_timeunit=e_chrono,
        date_start=Date.objects.create(day=None, season=None, year=9501),
        date_end=None,
    )
    e_era.known_directly.set(*[Profile.objects.filter(status=Q(status='active_player') | Q(status='inactive_player') | Q(status='dead_player'))])
    e_era.primary_locations.add(PrimaryLocation.objects.get(name='Hyllemath'))
    e_era.save()

    # Create PERIOD
    e_period = Period.objects.create(
        name='Archonat Nemetha Samatiana',
        name_genetive='Nowej Ery',
        description_short=None,
        description_long=None,
        in_timeunit=e_era,
        date_start=Date.objects.create(day=None, season=None, year=480),
        date_end=None,
    )
    e_period.known_directly.set(*[Profile.objects.filter(status=Q(status='active_player') | Q(status='inactive_player') | Q(status='dead_player'))])
    e_period.primary_locations.add(PrimaryLocation.objects.get(name='Hyllemath'))
    e_period.secondary_locations.add(SecondaryLocation.objects.get(name='Skadia'))
    e_period.save()
    print('HURRRRRRRRRRAY\n' * 50)
    
    # TODO - delete all redundantly created instances of Chronology, Era, Period - otherwise .get() will return > 1
    

    # for chronicle_event in ChronicleEvent_H.objects.all():
    #     failed = []
    #     try:
    #         sing_event = GameEvent.objects.create(
    #             name=None,
    #             name_genetive=None,
    #             description_short=None,
    #             description_long=chronicle_event.description,
    #             in_timeunit=TimeUnit.objects.get(name='Archonat Nemetha Samatiana'),
    #             date_start=None,
    #             date_end=None,
    #             game=GameSession.objects.get(title=chronicle_event.game.title),
    #             event_no_in_game=chronicle_event.event_no_in_game,
    #             debate=chronicle_event.debate,
    #         )
    #         sing_event.known_directly.set(*[chronicle_event.participants.all()])
    #         sing_event.known_indirectly.set(*[chronicle_event.informed.all()])
    #         sing_event.pictures.set(*[chronicle_event.pictures.all()])
    #         sing_event.save()
    #         print(f'Sukces: {chronicle_event.description[:50]}')
    #     except Exception as exc:
    #         failed += f'{chronicle_event.game.title}{chronicle_event.description[:20]}'
    #     print(failed)
    
    return redirect('home:dupa')
    # TODO - reconnect events that took place before 'Archonat Nemetha Samatiana ' to other Periods etc.