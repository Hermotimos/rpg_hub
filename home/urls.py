from django.urls import path

from home import views


from functools import wraps
def get_profile(view):
    @wraps(view)
    def wrap(request, *args, **kwargs):
        from users.models import Profile
        # print(view.context)
        # TODO how to extend context dict in a decorator
        # context['profile'] = Profile.objects.get(id=request.session['profile_id'])
        return view(request,  *args, **kwargs)

    return wrap


app_name = 'home'
urlpatterns = [
    # path('', get_profile(views.home_view), name='home'),
    path('', views.home_view, name='home'),
    path('dupa/', views.dupa_view, name='dupa'),
]

