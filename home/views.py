from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render

from prosoponomikon.models import Character
from rpg_project.utils import sample_from_qs
from toponomikon.models import Location


@login_required
def home_view(request):
    profile = request.user.profile

    known_characters = profile.characters_all_known_annotated_if_indirectly()
    known_characters = known_characters.exclude(profile=profile)
    known_characters = known_characters.select_related('profile')
    known_characters = known_characters.prefetch_related(
        'known_directly', 'known_indirectly', 'first_name')
    
    known_locations = Location.objects.select_related('main_image__image')
    known_locations = known_locations.prefetch_related(
        'known_directly', 'known_indirectly')

    if profile.status != 'gm':
        known_characters = known_characters.filter(
            Q(known_directly=profile) | Q(known_indirectly=profile))
        known_locations = known_locations.filter(
            Q(known_directly=profile) | Q(known_indirectly=profile))
        
    # set() ensures that if len(known) < k, than duplicates will be removed
    rand_characters = sample_from_qs(qs=known_characters, max_size=4)
    rand_locations = sample_from_qs(qs=known_locations, max_size=4)

    context = {
        'page_title': 'Hyllemath',
        'rand_characters': rand_characters,
        'rand_locations': rand_locations,
    }
    return render(request, 'home/home.html', context)


@login_required
def dupa_view(request):
    return render(request, 'home/dupa.html', {'page_title': 'Dupa!'})


