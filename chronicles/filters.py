import django_filters as filters
from chronicles.models import GameEvent, Thread, Location, GameSession, Profile


class GameEventFilter(filters.FilterSet):
    
    # def __init__(self, profile, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.profile = profile

    # TODO Access the 'events' queryset that is provided to the WHOLE FILTER
    # TODO and then do: threads queryset = 'events'.threads or Thread.filter(event__in=enents) etc.

    # Fields matching model fields:
    description_short = filters.CharFilter(lookup_expr='icontains', label="Szukaj w opisie wydarzenia w Kalendarium:")
    description_long = filters.CharFilter(lookup_expr='icontains', label="Szukaj w opisie wydarzenia w Kronice:")
    threads = filters.ModelMultipleChoiceFilter(queryset=Thread.objects.all(), label="Wątki:")
    locations = filters.ModelMultipleChoiceFilter(queryset=Location.objects.all(), label="Lokacje:")
    game = filters.ModelMultipleChoiceFilter(queryset=GameSession.objects.all(), label="Sesje:")
    known_directly = filters.ModelMultipleChoiceFilter(queryset=Profile.objects.filter(status__icontains='player'), label="Uczestnicy:")
    
    class Meta:
        model = GameEvent
        fields = []

