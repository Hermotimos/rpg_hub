from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, pagination, serializers, viewsets

from communications.models import Statement, Thread, ThreadTag
from rpg_project.utils import clear_cache
from users.models import Profile


class StatementSerializer(serializers.ModelSerializer):

    class Meta:
        model = Statement
        exclude = []


class StatementViewSet(viewsets.ModelViewSet):
    queryset = Statement.objects.prefetch_related(
        'seen_by__character',
        'seen_by__user',
        'options',
        'thread__participants',
        'thread__followers',
        'thread__tags',
        'author__user',
        'author__character',
    )
    serializer_class = StatementSerializer
    # DEFAULT_FILTER_BACKENDS in settings.py together with
    # 'filter_backends' and 'filterset_fields' enable filtering by:
    # http://127.0.0.1:8000/api/statements/?thread_id=48
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['thread_id']


# -----------------------------------------------------------------------------


class StatementByThreadListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Statement
        fields = ['text']

    def to_representation(self, instance):
        """Include some of the related objects' data as nested data."""
        representation = super().to_representation(instance)
        representation['id'] = instance.id
        representation['thread_obj'] = {
            'kind': instance.thread.kind,
            'is_ended': instance.thread.is_ended,
        }
        representation['author_obj'] = {
            'id': instance.author.id,
            'status': instance.author.status,
            'image': {'url': instance.author.image.url},
            'character': {'fullname': instance.author.character.fullname},
            'user': {
                'username': instance.author.user.username,
                'image': {'url': instance.author.user_image.url}
            },
        }
        representation['created_datetime'] = instance.created_at.strftime('%Y-%m-%d | %H:%M'),
        representation['seen_by_objs'] = [
            {
                'id': seen_by.id,
                'character': {'fullname': seen_by.character.fullname},
                'image': {'url': seen_by.image.url},
                'user': {
                    'username': seen_by.user.username,
                    'image': {'url': seen_by.user_image.url}
                },
            }
            for seen_by in instance.seen_by.all()
        ]
        image = getattr(instance, 'image', None)
        representation['image_obj'] = {'url': image.url if image else ''}

        return representation


class LargeResultsSetPagination(pagination.PageNumberPagination):
    """A custom Pagination class to ensure retrieval of all data"""
    page_size = 10000
    page_size_query_param = 'page_size'
    max_page_size = 10000


class StatementByThreadList(generics.ListAPIView):
    """
    A custom DRF view for filtering Statements by their Thread.
    This also requires a path registered in project URLs:
    re_path('^api/statements/thread/(?P<thread_id>\d+)/$', StatementByThreadList.as_view()),

    This enables filtering by:
    http://127.0.0.1:8000/api/statements/thread/48/

    """
    serializer_class = StatementByThreadListSerializer
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):
        thread_id = self.kwargs['thread_id']
        return Statement.objects.filter(
            thread_id=thread_id
        ).prefetch_related(
            'seen_by__character',
            'seen_by__user',
            'options',
            'thread__participants',
            'thread__followers',
            'thread__tags',
            'author__user',
            'author__character',
        )

    def post(self, request, *args, **kwargs):
        current_profile = Profile.objects.get(id=request.data['currentProfileId'])
        thread = Thread.objects.get(id=request.data['threadId'])
        statements = Statement.objects.filter(thread=thread.id).order_by('created_at')

        # # Update all statements to be seen by the profile
        if (
            current_profile in thread.participants.all()
            or current_profile.status == 'gm'
        ):
            SeenBy = Statement.seen_by.through
            relations = []
            for statement in statements.exclude(seen_by=current_profile):
                relations.append(SeenBy(statement_id=statement.id, profile_id=current_profile.id))
            SeenBy.objects.bulk_create(relations, ignore_conflicts=True)

            # If SeenBy has been changed, clear appropriate cache for the user
            # bulk_create() doesn't use model's save()  so no signals are fired
            # https://docs.djangoproject.com/en/4.2/ref/models/querysets/#bulk-create
            if relations:
                if thread.kind == 'Announcement':
                    clear_cache(cachename='navbar', vary_on_list=[[current_profile.user.id]])
                elif thread.kind == 'Debate':
                    clear_cache(cachename='sidebar', vary_on_list=[[current_profile.user.id]])

        return self.list(request, *args, **kwargs)


# -----------------------------------------------------------------------------


class ThreadSerializer(serializers.HyperlinkedModelSerializer):
    # statements = StatementSerializer(many=True, read_only=True)
    # This field together with ThreadViewSet.queryset optimizations enables nested data

    class Meta:
        model = Thread
        exclude = []


class ThreadViewSet(viewsets.ModelViewSet):
    queryset = Thread.objects.prefetch_related(
        'participants',
        'followers',
        'statements__seen_by',
        'statements__author',
        'statements__thread',
        'statements__options',
        'statements__options',
        'tags',
    )
    serializer_class = ThreadSerializer


# -----------------------------------------------------------------------------


class ThreadTagSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ThreadTag
        exclude = []


class ThreadTagViewSet(viewsets.ModelViewSet):
    queryset = ThreadTag.objects.all()
    serializer_class = ThreadTagSerializer


# -----------------------------------------------------------------------------
