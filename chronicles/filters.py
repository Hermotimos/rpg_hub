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
    current_profile = request.current_profile
    objects = PlotThread.objects.all()
    if not current_profile.can_view_all:
        objects = objects.filter(
            Q(events__participants=current_profile)
            | Q(events__informees=current_profile)
        )
    return objects.distinct()


def locations(request):
    current_profile = request.current_profile
    objects = Location.objects.all()
    if not current_profile.can_view_all:
        objects = objects.filter(
            Q(events__participants=current_profile)
            | Q(events__informees=current_profile)
        )
    return objects.distinct()


def participants(request):
    current_profile = request.current_profile
    objects = Profile.non_gm.all()
    if not current_profile.can_view_all:
        # Get profiles that know directly the same events as the current one
        objects = objects.filter(
            events_participated__in=current_profile.events_participated.all()
        )
    return objects.distinct().select_related().prefetch_related('character', 'user')


def games(request):
    current_profile = request.current_profile
    objects = GameSession.objects.all()
    if not current_profile.can_view_all:
        objects = objects.filter(
            Q(game_events__participants=current_profile)
            | Q(game_events__informees=current_profile)
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
        field_name='participants',
        queryset=participants,
        label="Uczestnicy:")
    games = ModelMultipleChoiceFilter(
        field_name='game',
        queryset=games,
        label="Sesje:")

    class Meta:
        model = GameEvent
        fields = []


# -----------------------------------------------------------------------------


def add_sublocations(request):
    """Modify locations filter result to include sublocations."""
    all_locs_ids = []
    for loc_id in request.GET.getlist('locations'):
        sublocations = Location.objects.get(id=loc_id).with_sublocations()
        all_locs_ids.extend([s.id for s in sublocations])

    request.GET = request.GET.copy()
    request.GET.setlist('locations', all_locs_ids)
    return request
