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


@login_required
def timeline_main_view(request):
    if request.user.profile in Profile.objects.filter(character_status='gm'):
        queryset = TimelineEvent.objects.all()
    else:
        participated_qs = Profile.objects.get(user=request.user).events_participated.all()
        informed_qs = Profile.objects.get(user=request.user).events_informed.all()
        queryset = (participated_qs | informed_qs).distinct()

    # years
    years_set = {e.year for e in queryset.all()}
    years_sorted_list = list(years_set)
    years_sorted_list.sort()

    # years with their seasons
    years_with_seasons_dict = {}
    for y in years_sorted_list:
        seasons_set = {e.season for e in queryset.all() if e.year == y}
        seasons_sorted_list = list(seasons_set)
        seasons_sorted_list.sort()
        years_with_seasons_dict[y] = seasons_sorted_list

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
    spec_locs_set = set()
    spec_locs_querysets_list = [event.specific_locations.all() for event in queryset]
    for qs in spec_locs_querysets_list:
        for sl in qs:
            spec_locs_set.add(sl)
    spec_locs_name_and_obj_list = [(t.name, t) for t in spec_locs_set]
    spec_locs_name_and_obj_list.sort()

    # general locations with their specific locations: LEFT UNSORTED TO REFLECT SUBSEQUNT GENERAL LOCATIONS IN GAME
    gen_locs_set = {event.general_location for event in queryset}
    gen_locs_with_spec_locs_list = []
    for gl in gen_locs_set:
        gen_loc_with_spec_locs_list = [gl, [sl for sl in spec_locs_name_and_obj_list if sl[1].general_location == gl]]
        gen_locs_with_spec_locs_list.append(gen_loc_with_spec_locs_list)

    context = {
        'page_title': 'Kalendarium',
        'seasons_with_styles_dict': SEASONS_WITH_STYLES_DICT,
        'years': years_sorted_list,
        'years_with_seasons_dict': years_with_seasons_dict,
        'threads': threads_name_and_obj_list,
        'participants': participants_name_and_obj_list,
        'gen_locs_with_spec_locs_list': gen_locs_with_spec_locs_list,
        'queryset': queryset
    }
    return render(request, 'history/timeline_main.html', context)


@login_required
def timeline_all_events_view(request):
    if request.user.profile in Profile.objects.filter(character_status='gm'):
        queryset = TimelineEvent.objects.all()
    else:
        participated_qs = Profile.objects.get(user=request.user).events_participated.all()
        informed_qs = Profile.objects.get(user=request.user).events_informed.all()
        queryset = (participated_qs | informed_qs).distinct()

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

    if request.user.profile in Profile.objects.filter(character_status='gm'):
        queryset = events_by_thread_qs
    else:
        participated_qs = Profile.objects.get(user=request.user).events_participated.all()
        informed_qs = Profile.objects.get(user=request.user).events_informed.all()
        events_by_user = (participated_qs | informed_qs).distinct()
        queryset = [e for e in events_by_user if e in events_by_thread_qs]

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

    if request.user.profile in Profile.objects.filter(character_status='gm'):
        queryset = events_by_participant_qs
    else:
        participated_qs = Profile.objects.get(user=request.user).events_participated.all()
        informed_qs = Profile.objects.get(user=request.user).events_informed.all()
        events_by_user = (participated_qs | informed_qs).distinct()
        queryset = [e for e in events_by_user if e in events_by_participant_qs]

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

    if request.user.profile in Profile.objects.filter(character_status='gm'):
        queryset = events_by_general_location_qs
    else:
        participated_qs = Profile.objects.get(user=request.user).events_participated.all()
        informed_qs = Profile.objects.get(user=request.user).events_informed.all()
        events_by_user = (participated_qs | informed_qs).distinct()
        queryset = [e for e in events_by_user if e in events_by_general_location_qs]

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

    if request.user.profile in Profile.objects.filter(character_status='gm'):
        queryset = events_by_specific_location_qs
    else:
        participated_qs = Profile.objects.get(user=request.user).events_participated.all()
        informed_qs = Profile.objects.get(user=request.user).events_informed.all()
        events_by_user = (participated_qs | informed_qs).distinct()
        queryset = [e for e in events_by_user if e in events_by_specific_location_qs]

    context = {
        'page_title': f'Kalendarium: {specific_location.name}',
        'header': f'{specific_location.name}... Jak odcisnęło się na Twoim losie to miejsce?',
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

    if request.user.profile in Profile.objects.filter(character_status='gm'):
        queryset = events_qs
    else:
        participated_qs = Profile.objects.get(user=request.user).events_participated.all()
        informed_qs = Profile.objects.get(user=request.user).events_informed.all()
        events_by_user = (participated_qs | informed_qs).distinct()
        queryset = [e for e in events_by_user if e in events_qs]

    context = {
        'page_title': page_title,
        'header': f'Nie wydaje się to wcale aż tak dawno temu...',
        'queryset': queryset,
        'seasons_with_styles_dict': SEASONS_WITH_STYLES_DICT,
    }
    return render(request, 'history/timeline_events.html', context)


@login_required
def create_event_view(request):
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

    participants = ', '.join(p.character_name.split(' ', 1)[0] for p in obj.participants.all())
    already_informed = obj.informed.all()[::1]                  # enforces evaluation of lazy Queryset for message
    informed = ', '.join(p.character_name.split(' ', 1)[0] for p in already_informed)

    if request.method == 'POST':
        form = TimelineEventInformForm(request.POST, instance=obj)
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

            messages.info(request, f'Poinformowałeś wybrane postaci!')
            _next = request.POST.get('next', '/')
            return HttpResponseRedirect(_next)

    else:
        form = TimelineEventInformForm(instance=obj)

    context = {
        'page_title': 'Poinformuj o wydarzeniu',
        'form': form,
        'event': obj,
        'participants': participants,
        'informed': informed
    }
    return render(request, 'history/timeline_add_informed.html', context)


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
    return render(request, 'history/chronicle_chapters_all.html', context)


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
    return render(request, 'history/chronicle_main.html', context)


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
    return render(request, 'history/chronicle_chapter.html', context)


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

    participants = ', '.join(p.character_name.split(' ', 1)[0] for p in obj.participants.all())
    already_informed = obj.informed.all()[::1]                  # enforces evaluation of lazy Queryset for message
    informed = ', '.join(p.character_name.split(' ', 1)[0] for p in already_informed)

    if request.method == 'POST':
        form = ChronicleEventInformForm(request.POST, instance=obj)
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

            messages.info(request, f'Poinformowałeś wybrane postaci!')
            _next = request.POST.get('next', '/')
            return HttpResponseRedirect(_next)
    else:
        form = ChronicleEventInformForm(instance=obj)

    context = {
        'page_title': 'Poinformuj o wydarzeniu',
        'form': form,
        'event': obj,
        'participants': participants,
        'informed': informed
    }
    return render(request, 'history/chronicle_add_informed.html', context)


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