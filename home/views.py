from random import randrange

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View

from rpg_project.utils import query_debugger
from users.models import Profile


@query_debugger
@login_required
def home_view(request):
    profile = request.user.profile
    rand_profiles = []

    if profile.character_status == 'gm':
        known_profiles = Profile.objects.exclude(id=profile.id)
    # else:
    #     known_profiles = [profile]

        rand_profiles = []
        rand_nums = []
        counter = 0
        while counter < 4:
            rand = randrange(len(known_profiles))
            if rand not in rand_nums:
                rand_profiles.append(known_profiles[rand])
                rand_nums.append(rand)
                counter += 1

    context = {
        'page_title': 'Hyllemath',
        'rand_profiles': rand_profiles,
    }
    return render(request, 'home/home.html', context)


# @query_debugger
# @login_required
# def dupa_view(request):
#     return render(request, 'home/dupa.html', {'page_title': 'Dupa!'})


class DupaView(View):

    @method_decorator(login_required)
    def get(self, request):
        return render(request, 'home/dupa.html', {'page_title': 'Dupa!'})
