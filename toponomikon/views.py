from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.shortcuts import redirect, render

from knowledge.models import KnowledgePacket, MapPacket
from rpg_project.utils import auth_profile, handle_inform_form
from toponomikon.models import Location, LocationType, SecondaryLocation


@login_required
@auth_profile(['all'])
def toponomikon_main_view(request):
    current_profile = request.current_profile

    known_locations = current_profile.locations_known_annotated()
    secondary_locs = SecondaryLocation.objects.filter(id__in=known_locations)
    primary_locations = known_locations.filter(in_location=None).prefetch_related(
        Prefetch('locations', queryset=secondary_locs))

    if current_profile.can_view_all:
        all_maps = MapPacket.objects.all()
    else:
        all_maps = current_profile.map_packets.all()

    context = {
        'page_title': 'Toponomikon',
        'primary_locations': primary_locations,
        'known_locations': known_locations,
        'all_maps': all_maps.prefetch_related('picture_sets__pictures'),
    }
    return render(request, 'toponomikon/main.html', context)


@login_required
@auth_profile(['all'])
def toponomikon_location_view(request, location_id):
    current_profile = request.current_profile

    known_locations = current_profile.locations_known_annotated()

    # THIS LOCATION
    if current_profile.can_view_all:
        knowledge_packets = KnowledgePacket.objects.prefetch_related(
            'picture_sets__pictures')
        locs = known_locations.prefetch_related(
            Prefetch('knowledge_packets', knowledge_packets.distinct()),
            'map_packets__picture_sets__pictures',
            'picture_sets__pictures',
            'characters__profile',
        )
    else:
        knowledge_packets = current_profile.knowledge_packets.prefetch_related(
            'picture_sets__pictures')
        locs = known_locations.prefetch_related(
            Prefetch('knowledge_packets', knowledge_packets.distinct()),
            Prefetch('map_packets', current_profile.map_packets.all()),
            'map_packets__picture_sets__pictures',
            'picture_sets__pictures',
        )
    locs = locs.select_related(
        'main_image', 'audio_set', 'in_location__in_location__in_location')
    try:
        this_location = locs.get(id=location_id)
    except Location.DoesNotExist:
        return redirect('users:dupa')

    # LOCATIONS TAB
    locations = known_locations.filter(in_location=this_location)
    locations = locations.prefetch_related(
        Prefetch('locations', queryset=known_locations))

    location_types = LocationType.objects.filter(locations__in=locations)
    location_types = location_types.prefetch_related(
        Prefetch('locations', queryset=locations))

    # ACQUAINTANCES TAB
    # Characters in this location and its sub-locations if known to profile:
    acquaintanceships = current_profile.character.acquaintanceships()
    acquaintanceships = acquaintanceships.filter(
        known_character__frequented_locations__in=this_location.with_sublocations()
    ).exclude(known_character=current_profile.character)

    if request.method == 'POST':
        handle_inform_form(request)

    context = {
        'page_title': this_location.name,
        'this_location': this_location,
        'location_types': location_types.distinct(),
        'informables': this_location.informables(current_profile),
        'acquaintanceships': acquaintanceships.distinct(),
    }
    if this_location in known_locations or current_profile.can_view_all:
        return render(request, 'toponomikon/this_location.html', context)
    else:
        return redirect('users:dupa')
