from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, serializers, viewsets

from communications.models import Statement, Thread


class StatementSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Statement
        exclude = []


class StatementViewSet(viewsets.ModelViewSet):
    queryset = Statement.objects.prefetch_related('seen_by', 'options')
    serializer_class = StatementSerializer
    # DEFAULT_FILTER_BACKENDS in settings.py together with
    # 'filter_backends' and 'filterset_fields' enable filtering by:
    # http://127.0.0.1:8000/api/statements/?thread_id=48
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['thread_id']


class StatementByThreadList(generics.ListAPIView):
    """
    A custom DRF view for filtering Statements by their Thread.
    This also requires a path registered in project URLs:
    re_path('^api/statements/thread/(?P<thread_id>\d+)/$', StatementByThreadList.as_view()),

    This enables filtering by:
    http://127.0.0.1:8000/api/statements/thread/48/

    """
    serializer_class = StatementSerializer

    def get_queryset(self):
        thread_id = self.kwargs['thread_id']
        return Statement.objects.filter(thread_id=thread_id)


# -----------------------------------------------------------------------------


class ThreadSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Thread
        exclude = []


class ThreadViewSet(viewsets.ModelViewSet):
    queryset = Thread.objects.all()
    serializer_class = ThreadSerializer


# -----------------------------------------------------------------------------
