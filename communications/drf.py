from rest_framework import serializers, viewsets
from communications.models import Statement, Thread


class StatementSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Statement
        exclude = []


class StatementViewSet(viewsets.ModelViewSet):
    queryset = Statement.objects.prefetch_related('seen_by', 'options')
    serializer_class = StatementSerializer


# -----------------------------------------------------------------------------


class ThreadSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Thread
        exclude = []


class ThreadViewSet(viewsets.ModelViewSet):
    queryset = Thread.objects.all()
    serializer_class = ThreadSerializer


# -----------------------------------------------------------------------------
