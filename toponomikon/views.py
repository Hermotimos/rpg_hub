from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch, When, Case, Value, IntegerField
from django.shortcuts import render, redirect

from rpg_project.utils import handle_inform_form
from knowledge.models import MapPacket
from toponomikon.models import Location, LocationType, PrimaryLocation, \
    SecondaryLocation


@login_required
def toponomikon_main_view(request):
    profile = request.user.profile
    if profile.status == 'gm':
        primary_locs = PrimaryLocation.objects.prefetch_related('locations')
        all_locs = Location.objects.values('name')
        all_maps = MapPacket.objects.all()
    else:
        known_dir = profile.locs_known_directly.all()
        known_indir = profile.locs_known_indirectly.all()
        known_only_indir = known_indir.exclude(id__in=known_dir)
        all_known = (known_dir | known_indir)
        
        primary_locs = PrimaryLocation.objects.filter(id__in=all_known)
        primary_locs = primary_locs.prefetch_related(
            Prefetch(
                'locations',
                queryset=SecondaryLocation.objects.filter(id__in=all_known)
            )
        )
        primary_locs = primary_locs.annotate(
            only_indirectly=Case(
                When(id__in=known_only_indir, then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            ),
        )
        all_locs = Location.objects.values('name').filter(id__in=all_known)
        all_maps = profile.map_packets.all()
    
    context = {
        'page_title': 'Toponomikon',
        'primary_locs': primary_locs.select_related('main_image'),
        'all_locs': all_locs,
        'all_maps': all_maps.prefetch_related('pictures'),
    }
    return render(request, 'toponomikon/main.html', context)

    
@login_required
def toponomikon_location_view(request, loc_name):
    profile = request.user.profile
    known_dir = profile.locs_known_directly.all()
    known_indir = profile.locs_known_indirectly.all()
    known_only_indir = known_indir.exclude(id__in=known_dir)
    known_all = (known_dir | known_indir).distinct()
    
    # THIS LOCATION
    prep = Location.objects.select_related(
        'main_image', 'audio_set', 'in_location__in_location__in_location')
    
    if profile.status == 'gm':
        prep = prep.prefetch_related(
            'knowledge_packets__pictures',
            'map_packets__pictures',
            'pictures',
            'frequented_by_characters__profile',
        )
    else:
        prep = prep.prefetch_related(
            Prefetch('knowledge_packets', profile.knowledge_packets.all()),
            Prefetch('map_packets', profile.map_packets.all()),
            'knowledge_packets__pictures',
            'map_packets__pictures',
            'pictures',
        )
        prep = prep.annotate(
            only_indirectly=Case(
                When(id__in=known_only_indir, then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            )
        )
        
    this_location = prep.get(name=loc_name)
    page_title = this_location.name
    
    # CHARACTERS TAB
    # Characters in this location and its sub-locations if known to profile:
    characters = profile.characters_all_known_annotated_if_indirectly()
    characters = characters.filter(
        frequented_locations__in=this_location.with_sublocations())
    characters = characters.select_related('profile')
    characters = characters.prefetch_related('known_directly')
    
    # LOCATIONS TAB
    if profile.status == 'gm':
        locations = this_location.locations.prefetch_related('locations')
    else:
        locations = this_location.locations.filter(id__in=known_all)
        locations = locations.prefetch_related(
            Prefetch('locations', queryset=known_all)
        )
        locations = locations.annotate(
            only_indirectly=Case(
                When(id__in=known_only_indir, then=Value(1)),
                default=Value(0),
                output_field=IntegerField()
            )
        )
    locations = locations.select_related('main_image__image')
    locations = locations.distinct()
    
    location_types = LocationType.objects.filter(locations__in=locations)
    location_types = location_types.prefetch_related(
        Prefetch('locations', queryset=locations)
    )
    location_types = location_types.distinct()

    if request.method == 'POST':
        handle_inform_form(request)
        
    context = {
        'page_title': page_title,
        'this_location': this_location,
        'location_types': location_types,
        'characters': characters.distinct(),
    }
    if this_location in known_all or profile.status == 'gm':
        return render(request, 'toponomikon/this_location.html', context)
    else:
        return redirect('home:dupa')
