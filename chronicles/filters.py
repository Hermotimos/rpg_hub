from django.db.models import Q
from django_filters import (
    CharFilter,
    FilterSet,
    ModelMultipleChoiceFilter,
)

from chronicles.models import GameEvent, Thread, Location, GameSession, Profile


def threads(request):
    profile = request.user.profile
    objects = Thread.objects.all()
    if profile.status != 'gm':
        objects = objects.filter(
            Q(events__known_directly=profile)
            | Q(events__known_indirectly=profile)
        )
    return objects.distinct()


def locations(request):
    profile = request.user.profile
    objects = Location.objects.all()
    if profile.status != 'gm':
        objects = objects.filter(
            Q(events__known_directly=profile)
            | Q(events__known_indirectly=profile)
        )
    return objects.distinct()


def participants(request):
    profile = request.user.profile
    # objects = Profile.objects.filter(status__icontains='player')
    objects = Profile.players.all()
    if profile.status != 'gm':
        # Get profiles that know directly the event that profile knows directly
        objects = objects.filter(
            events_known_directly__in=profile.events_known_directly.all()
        )
    return objects.distinct().select_related()


def games(request):
    profile = request.user.profile
    objects = GameSession.objects.all()
    if profile.status != 'gm':
        objects = objects.filter(
            Q(game_events__known_directly=profile)
            | Q(game_events__known_indirectly=profile)
        )
    return objects.distinct().select_related()


class GameEventFilter(FilterSet):
    description_short = CharFilter(
        lookup_expr='icontains',
        label="Wydarzenie w Kalendarium:",
    )
    description_long = CharFilter(
        lookup_expr='icontains',
        label="Wydarzenie w Kronice:",
    )
    threads = ModelMultipleChoiceFilter(queryset=threads, label="Wątki:")
    locations = ModelMultipleChoiceFilter(queryset=locations, label="Lokacje:")
    participants = ModelMultipleChoiceFilter(
        field_name='known_directly',
        queryset=participants,
        label="Uczestnicy:",
    )
    games = ModelMultipleChoiceFilter(
        field_name='game',
        queryset=games,
        label="Sesje:",
    )

    class Meta:
        model = GameEvent
        fields = []
