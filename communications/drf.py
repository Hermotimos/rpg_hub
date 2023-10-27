from rest_framework import serializers, viewsets
from communications.models import Statement, Thread
from rest_framework import generics


class StatementSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Statement
        exclude = []


class StatementViewSet(viewsets.ModelViewSet):
    queryset = Statement.objects.prefetch_related('seen_by', 'options')
    serializer_class = StatementSerializer


class StatementByThreadList(generics.ListAPIView):
    """A custom DRF view for filtering Statements by their Thread."""
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
