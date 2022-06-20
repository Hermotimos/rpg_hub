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
    current_profile = Profile.objects.get(id=request.session['profile_id'])

    known_locations = current_profile.locations_known_annotated()
    all_locs = Location.objects.values('name').filter(id__in=known_locations)

    secondary_locs = SecondaryLocation.objects.filter(id__in=known_locations)
    primary_locs = known_locations.filter(in_location=None)
    primary_locs = primary_locs.prefetch_related(
        Prefetch('locations', queryset=secondary_locs))

    if current_profile.can_view_all:
        all_maps = MapPacket.objects.all()
    else:
        all_maps = current_profile.map_packets.all()
    
    context = {
        'current_profile': current_profile,
        'page_title': 'Toponomikon',
        'primary_locs': primary_locs,
        'all_locs': all_locs,
        'all_maps': all_maps.prefetch_related('picture_sets__pictures'),
    }
    return render(request, 'toponomikon/main.html', context)

    
@login_required
def toponomikon_location_view(request, loc_name):
    current_profile = Profile.objects.get(id=request.session['profile_id'])

    known_locations = current_profile.locations_known_annotated()
    
    # THIS LOCATION
    if current_profile.can_view_all:
        locs = known_locations.prefetch_related(
            'knowledge_packets__picture_sets__pictures',
            'map_packets__picture_sets__pictures',
            'picture_sets__pictures',
            'characters__profile',
        )
    else:
        locs = known_locations.prefetch_related(
            Prefetch('knowledge_packets', current_profile.knowledge_packets.all()),
            Prefetch('map_packets', current_profile.map_packets.all()),
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

    # ACQUAINTANCES TAB
    # Characters in this location and its sub-locations if known to profile:
    acquaintanceships = current_profile.character.acquaintanceships()
    acquaintanceships = acquaintanceships.filter(
        known_character__frequented_locations__in=this_location.with_sublocations())

    if request.method == 'POST':
        handle_inform_form(request)
        
    context = {
        'current_profile': current_profile,
        'page_title': this_location.name,
        'this_location': this_location,
        'location_types': location_types.distinct(),
        'acquaintanceships': acquaintanceships.distinct(),
    }
    if this_location in known_locations or current_profile.can_view_all:
        return render(request, 'toponomikon/this_location.html', context)
    else:
        return redirect('users:dupa')
