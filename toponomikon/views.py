from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch, Q, When, Case, Value, IntegerField
from django.shortcuts import render, redirect, get_object_or_404

from knowledge.models import KnowledgePacket
from rpg_project.utils import send_emails
from toponomikon.models import Location, LocationType, PrimaryLocation, SecondaryLocation


@login_required
def toponomikon_main_view(request):
    profile = request.user.profile
    known_only_indirectly = profile.locs_known_indirectly.exclude(
        id__in=profile.locs_known_directly.all()
    )
    if profile.status == 'gm':
        locations = PrimaryLocation.objects.all()
    else:
        locations = PrimaryLocation.objects.filter(
            Q(id__in=profile.locs_known_directly.all())
            | Q(id__in=profile.locs_known_indirectly.all())
        )
    locations = locations.prefetch_related('locations')
    locations = locations.select_related('main_image', 'location_type')
    locations = locations.annotate(only_indirectly=Case(
        When(id__in=known_only_indirectly, then=Value(1)),
        default=Value(0),
        output_field=IntegerField()
    ))
    
    context = {
        'page_title': 'Toponomikon',
        'locations': locations,
    }
    return render(request, 'toponomikon/toponomikon_main.html', context)


@login_required
def toponomikon_location_view(request, loc_name):
    profile = request.user.profile
    location = get_object_or_404(Location, name=loc_name)
    
    directly = location.known_directly.all()
    indirectly = location.known_indirectly.all()
    allowed = (directly | indirectly)
    
    if profile in indirectly and profile not in directly and profile.status != 'gm':
        loc_known_indirectly = True
        page_title = location.name + ' (znasz z opowieści)'
    else:
        loc_known_indirectly = False
        page_title = location.name

    # TABS
    if profile.status == 'gm':
        locations = location.locations.all()
        kn_packets = location.knowledge_packets.all()
    else:
        known_directly = location.locations.filter(known_directly=profile)
        known_indirectly = location.locations.filter(
            known_indirectly=profile).exclude(id__in=known_directly)
        locations = (known_directly | known_indirectly)
        kn_packets = location.knowledge_packets.filter(acquired_by=profile)
    
    only_indirectly = profile.locs_known_indirectly.exclude(
        id__in=profile.locs_known_directly.all()
    )
    locations = locations\
        .select_related('main_image', 'location_type')\
        .distinct() \
        .annotate(
            only_indirectly=Case(
                When(id__in=only_indirectly, then=Value(1)),
                default=Value(0),
                output_field=IntegerField()
            )
        ) \
        .distinct()

    location_types = LocationType.objects\
        .filter(locations__in=locations)\
        .prefetch_related(Prefetch('locations', queryset=locations))\
        .distinct()
    
    # INFORM LOCATION
    # dict(request.POST).items() == < QueryDict: {
    #     'csrfmiddlewaretoken': ['KcoYDwb7r86Ll2SdQUNrDCKs...'],
    #     '2': ['on'],
    #     'location': ['']
    # } >
    if request.method == 'POST' and 'location' in request.POST:
        data = dict(request.POST)
        informed_ids = [k for k, v_list in data.items() if 'on' in v_list]
        location.known_indirectly.add(*informed_ids)
        
        send_emails(request, informed_ids, location=location)
        if informed_ids:
            messages.info(request, f'Poinformowano wybrane postaci!')
    
    # INFORM KNOWLEDGE PACKETS
    # dict(request.POST).items() == < QueryDict: {
    #   'csrfmiddlewaretoken': ['42GqawP0aa5WOfpuTkKixYsROBaKSQng...'],
    #   '2': ['on'],
    #   'kn_packet': ['38']
    # } >
    elif request.method == 'POST' and 'kn_packet' in request.POST:
        data = dict(request.POST)
        informed_ids = [k for k, v_list in data.items() if 'on' in v_list]
        kn_packet_id = data['kn_packet'][0]
        kn_packet = KnowledgePacket.objects.get(id=kn_packet_id)
        kn_packet.acquired_by.add(*informed_ids)
        
        send_emails(request, informed_ids, kn_packet=kn_packet)
        if informed_ids:
            messages.info(request, f'Poinformowano wybrane postaci!')

    context = {
        # General
        'page_title': page_title,
        'location': location,
        'loc_known_indirectly': loc_known_indirectly,
        # Tabs
        'kn_packets': kn_packets,
        'locations': locations,
        'location_types': location_types,
        'pictures': location.pictures.all(),
    }
    if profile in allowed or profile.status == 'gm':
        return render(request, 'toponomikon/this_location.html', context)
    else:
        return redirect('home:dupa')
