import debug_toolbar
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from rest_framework import routers
from strawberry.django.views import GraphQLView

from communications.drf import (
    StatementByThreadList, StatementViewSet, ThreadViewSet,
)
from rpg_project.schema import schema
from users.drf import GroupViewSet, ProfileViewSet, UserViewSet

admin.site.enable_nav_sidebar = False
admin.site.index_title = "Hyllemath CMS"
admin.site.site_header = "Hyllemath"
admin.site.site_title = "1.0"


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('users.urls')),
    # path('associations/', include('associations.urls')),
    path('chronicles/', include('chronicles.urls')),
    path('communications/', include('communications.urls')),
    path('contact/', include('contact.urls')),
    path('knowledge/', include('knowledge.urls')),
    path('technicalities/', include('technicalities.urls')),
    path('rules/', include('rules.urls')),
    path('toponomikon/', include('toponomikon.urls')),
    path('prosoponomikon/', include('prosoponomikon.urls')),

    path('__debug__/', include(debug_toolbar.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# ----------------------------------------------------------------------------
# Django REST Framework URLs

router = routers.DefaultRouter()
router.register(r'groups', GroupViewSet)
router.register(r'users', UserViewSet)
router.register(r'profiles', ProfileViewSet)
router.register(r'statements', StatementViewSet)
router.register(r'threads', ThreadViewSet)

urlpatterns += [
    # REST API root: http://127.0.0.1:8000/api/
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # communications
    re_path('^api/statements/thread/(?P<thread_id>\d+)/$', StatementByThreadList.as_view()),
]


# ----------------------------------------------------------------------------
# Strawberry Django URLs

urlpatterns += [
    # GraphQL API root: http://127.0.0.1:8000/graphql/
    path('graphql/', GraphQLView.as_view(
        graphiql=settings.DEBUG,    # turn off Graphiql when DEBUG=False
        schema=schema)),
]
