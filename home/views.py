from random import randrange

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from users.models import Profile


@login_required
def home_view(request):
    profile = request.user.profile
    if profile.status == 'gm':
        known_profiles = Profile.objects.exclude(id=profile.id)
    else:
        known_profiles = []
        
    rand_profiles = rand_nums = []
    counter = 0
    
    if known_profiles:
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


@login_required
def dupa_view(request):
    return render(request, 'home/dupa.html', {'page_title': 'Dupa!'})


