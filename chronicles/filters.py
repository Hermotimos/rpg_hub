from django.db.models import Q
from django.forms.widgets import TextInput
from django_filters import (
    CharFilter,
    FilterSet,
    ModelMultipleChoiceFilter,
)

from chronicles.models import GameEvent, PlotThread, Location, GameSession
from users.models import Profile


def plot_threads(request):
    profile = Profile.objects.get(id=request.session['profile_id'])
    objects = PlotThread.objects.all()
    if not profile.can_view_all:
        objects = objects.filter(
            Q(events__known_directly=profile)
            | Q(events__known_indirectly=profile)
        )
    return objects.distinct()


def locations(request):
    profile = Profile.objects.get(id=request.session['profile_id'])
    objects = Location.objects.all()
    if not profile.can_view_all:
        objects = objects.filter(
            Q(events__known_directly=profile)
            | Q(events__known_indirectly=profile)
        )
    return objects.distinct()


def participants(request):
    profile = Profile.objects.get(id=request.session['profile_id'])
    objects = Profile.non_gm.all()
    if not profile.can_view_all:
        # Get profiles that know directly the same events as the current one
        objects = objects.filter(
            events_known_directly__in=profile.events_known_directly.all()
        )
    return objects.distinct().select_related()


def games(request):
    profile = Profile.objects.get(id=request.session['profile_id'])
    objects = GameSession.objects.all()
    if not profile.can_view_all:
        objects = objects.filter(
            Q(game_events__known_directly=profile)
            | Q(game_events__known_indirectly=profile)
        )
    return objects.distinct().select_related()


class GameEventFilter(FilterSet):
    description_short = CharFilter(
        lookup_expr='icontains',
        label="Wydarzenie w Kalendarium:",
        widget=TextInput(attrs={'placeholder': 'Szukaj w tekście Wydarzenia'}))
    description_long = CharFilter(
        lookup_expr='icontains',
        label="Wydarzenie w Kronice:",
        widget=TextInput(attrs={'placeholder': 'Szukaj w tekście Wydarzenia'}))
    plot_threads = ModelMultipleChoiceFilter(
        queryset=plot_threads,
        label="Wątki:")
    locations = ModelMultipleChoiceFilter(
        queryset=locations,
        label="Lokacje:")
    participants = ModelMultipleChoiceFilter(
        field_name='known_directly',
        queryset=participants,
        label="Uczestnicy:")
    games = ModelMultipleChoiceFilter(
        field_name='game',
        queryset=games,
        label="Sesje:")

    class Meta:
        model = GameEvent
        fields = []
