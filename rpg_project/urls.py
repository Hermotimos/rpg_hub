"""rpg_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

import debug_toolbar

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('characters/', include('characters.urls')),
    path('contact/', include('contact.urls')),
    path('debates/', include('debates.urls')),
    path('history/', include('history.urls')),
    path('knowledge/', include('knowledge.urls')),
    path('news/', include('news.urls')),
    path('reload/', include('reload.urls')),
    path('rules/', include('rules.urls')),
    path('toponomikon/', include('toponomikon.urls')),
    path('prosoponomikon/', include('prosoponomikon.urls')),
    path('users/', include('users.urls')),


]

# only for development phase (= when DEBUG is True), not suitable for production
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [path(r'__debug__', include(debug_toolbar.urls)), ]
    # was r'^__debug__' but Pycharm warned about it, so testing without ^
# WARNINGS:
# ?: (2_0.W001) Your URL pattern '^__debug__' has a route that contains '(?P<', begins with a '^', or ends with a '$'.
# This was likely an oversight when migrating to django.urls.path().
