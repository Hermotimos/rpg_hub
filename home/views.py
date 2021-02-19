from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render

from rpg_project.utils import sample_from_qs
from toponomikon.models import Location
from users.models import Profile


@login_required
def home_view(request):
    profile = request.user.profile

    known_profiles = Profile.objects.exclude(id=profile.id)
    known_profiles = known_profiles.select_related('character')
    known_profiles = known_profiles.prefetch_related(
        'character__known_directly', 'character__known_indirectly')
    
    known_locations = Location.objects.select_related('main_image')
    known_locations = known_locations.prefetch_related(
        'known_directly', 'known_indirectly')

    if profile.status != 'gm':
        known_profiles = known_profiles.filter(
            Q(character__known_directly=profile)
            | Q(character__known_indirectly=profile))
        known_locations = known_locations.filter(
            Q(known_directly=profile) | Q(known_indirectly=profile))
        
    # set() ensures that if len(known) < k, than duplicates will be removed
    rand_profiles = sample_from_qs(qs=known_profiles, max_size=4)
    rand_locations = sample_from_qs(qs=known_locations, max_size=4)

    context = {
        'page_title': 'Hyllemath',
        'rand_profiles': rand_profiles,
        'rand_locations': rand_locations,
    }
    return render(request, 'home/home.html', context)


@login_required
def dupa_view(request):
    return render(request, 'home/dupa.html', {'page_title': 'Dupa!'})


