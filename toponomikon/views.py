from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch, When, Case, Value, IntegerField
from django.shortcuts import render, redirect

from knowledge.models import MapPacket
from rpg_project.utils import handle_inform_form
from toponomikon.models import Location, LocationType, PrimaryLocation, \
    SecondaryLocation
from users.models import Profile


@login_required
def toponomikon_main_view(request):
    profile = Profile.objects.get(id=request.session['profile_id'])

    known_locations = profile.locations_known_annotated()
    all_locs = Location.objects.values('name').filter(id__in=known_locations)

    secondary_locs = SecondaryLocation.objects.filter(id__in=known_locations)
    primary_locs = known_locations.filter(in_location=None)
    primary_locs = primary_locs.prefetch_related(
        Prefetch('locations', queryset=secondary_locs))

    if profile.can_view_all:
        all_maps = MapPacket.objects.all()
    else:
        all_maps = profile.map_packets.all()
    
    context = {
        'current_profile': profile,
        'page_title': 'Toponomikon',
        'primary_locs': primary_locs,
        'all_locs': all_locs,
        'all_maps': all_maps.prefetch_related('picture_sets__pictures'),
    }
    return render(request, 'toponomikon/main.html', context)

    
@login_required
def toponomikon_location_view(request, loc_name):
    profile = Profile.objects.get(id=request.session['profile_id'])

    known_locations = profile.locations_known_annotated()
    
    # THIS LOCATION
    if profile.can_view_all:
        locs = known_locations.prefetch_related(
            'knowledge_packets__picture_sets__pictures',
            'map_packets__picture_sets__pictures',
            'picture_sets__pictures',
            'frequented_by_characters__profile',
        )
    else:
        locs = known_locations.prefetch_related(
            Prefetch('knowledge_packets', profile.knowledge_packets.all()),
            Prefetch('map_packets', profile.map_packets.all()),
            'knowledge_packets__picture_sets__pictures',
            'map_packets__picture_sets__pictures',
            'picture_sets__pictures',
        )
    locs = locs.select_related(
        'main_image', 'audio_set', 'in_location__in_location__in_location')
    try:
        this_location = locs.get(name=loc_name)
    except Location.DoesNotExist:
        return redirect('users:dupa')
    
    # LOCATIONS TAB
    locations = known_locations.filter(in_location=this_location)
    locations = locations.prefetch_related(
        Prefetch('locations', queryset=known_locations)
    )
    location_types = LocationType.objects.filter(locations__in=locations)
    location_types = location_types.prefetch_related(
        Prefetch('locations', queryset=locations))

    # CHARACTERS TAB
    # Characters in this location and its sub-locations if known to profile:
    characters = profile.characters_known_annotated()
    characters = characters.filter(
        frequented_locations__in=this_location.with_sublocations())

    if request.method == 'POST':
        handle_inform_form(request)
        
    context = {
        'current_profile': profile,
        'page_title': this_location.name,
        'this_location': this_location,
        'location_types': location_types.distinct(),
        'characters': characters.distinct(),
    }
    if this_location in known_locations or profile.can_view_all:
        return render(request, 'toponomikon/this_location.html', context)
    else:
        return redirect('users:dupa')
