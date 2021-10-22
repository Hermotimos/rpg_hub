from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from rpg_project.utils import sample_from_qs
from users.models import Profile


@login_required
def home_view(request):
    profile = Profile.objects.get(id=request.session['profile_id'])

    known_characters = profile.characters_all_known_annotated_if_indirectly()
    known_locations = profile.locations_all_known_annotated_if_indirectly()
    
    # set() ensures that if len(known) < k, than duplicates will be removed
    rand_characters = sample_from_qs(qs=known_characters, max_size=4)
    rand_locations = sample_from_qs(qs=known_locations, max_size=4)

    context = {
        'current_profile': profile,
        'page_title': 'Hyllemath',
        'rand_characters': rand_characters,
        'rand_locations': rand_locations,
    }
    return render(request, 'home/home.html', context)


@login_required
def dupa_view(request):
    profile = Profile.objects.get(id=request.session['profile_id'])
    context = {
        'current_profile': profile,
        'page_title': 'Dupa',
    }
    return render(request, 'home/dupa.html', context)


