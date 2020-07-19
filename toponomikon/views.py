from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch, Q, When, Case, Value, IntegerField
from django.shortcuts import render, redirect, get_object_or_404

from knowledge.models import KnowledgePacket
from rpg_project.utils import send_emails
from toponomikon.models import Location, LocationType, PrimaryLocation, \
    SecondaryLocation


@login_required
def toponomikon_main_view(request):
    profile = request.user.profile
    locations = PrimaryLocation.objects.prefetch_related('locations')
    
    if not profile.status == 'gm':
        known_only_indirectly = profile.locs_known_indirectly.exclude(
            id__in=profile.locs_known_directly.all()
        )
        locations = PrimaryLocation.objects.filter(
            Q(id__in=profile.locs_known_directly.all())
            | Q(id__in=profile.locs_known_indirectly.all())
        )
        locations = locations.prefetch_related(
            Prefetch(
                'locations',
                queryset=SecondaryLocation.objects.filter(
                    id__in=(profile.locs_known_directly.all()
                            | profile.locs_known_indirectly.all())
                )
            )
        )
        locations = locations.annotate(only_indirectly=Case(
            When(id__in=known_only_indirectly, then=Value(1)),
            default=Value(0),
            output_field=IntegerField(),
        ))
    
    locations = locations.select_related('main_image')
    
    context = {
        'page_title': 'Toponomikon',
        'locations': locations,
    }
    return render(request, 'toponomikon/toponomikon_main.html', context)


@login_required
def toponomikon_location_view(request, loc_name):
    profile = request.user.profile
    known_directly = profile.locs_known_directly.all()
    known_indirectly = profile.locs_known_indirectly.all()
    known_only_indirectly = known_indirectly.exclude(id__in=known_directly)
    known_all = (known_directly | known_indirectly).distinct()
    
    # Get this_location with prefetched data and annotations
    this_location = Location.objects.select_related('main_image')
    if profile.status == 'gm':
        this_location = this_location.prefetch_related(
            'knowledge_packets__pictures',
        )
    else:
        this_location = this_location.prefetch_related(
            Prefetch(
                'knowledge_packets',
                queryset=profile.knowledge_packets.all()
            ),
            'knowledge_packets__pictures',
            'pictures',
        )
    this_location = this_location.annotate(
        only_indirectly=Case(
            When(id__in=known_only_indirectly, then=Value(1)),
            default=Value(0),
            output_field=IntegerField(),
        )
    )
    this_location = this_location.get(name=loc_name)
    
    page_title = this_location.name
    if this_location in known_only_indirectly:
        page_title += ' (znasz z opowieści)'
    
    # TABS
    if profile.status == 'gm':
        locations = this_location.locations.prefetch_related('locations')
    else:
        locations = this_location.locations.filter(id__in=known_all)
        locations = locations.prefetch_related(
            Prefetch('locations', queryset=known_all)
        )
        locations = locations.annotate(
            only_indirectly=Case(
                When(id__in=known_only_indirectly, then=Value(1)),
                default=Value(0),
                output_field=IntegerField()
            )
        )
    locations = locations.select_related('main_image')
    locations = locations.distinct()
    
    location_types = LocationType.objects.filter(locations__in=locations)
    location_types = location_types.prefetch_related(
        Prefetch('locations', queryset=locations)
    )
    location_types = location_types.distinct()
    
    # INFORM LOCATION
    # dict(request.POST).items() == < QueryDict: {
    #     'csrfmiddlewaretoken': ['KcoYDwb7r86Ll2SdQUNrDCKs...'],
    #     '2': ['on'],
    #     'location': ['']
    # } >
    if request.method == 'POST' and 'location' in request.POST:
        data = dict(request.POST)
        informed_ids = [k for k, v_list in data.items() if 'on' in v_list]
        this_location.known_indirectly.add(*informed_ids)
        
        send_emails(request, informed_ids, location=this_location)
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
        'this_location': this_location,
        # Tabs
        'location_types': location_types,
    }
    if this_location in known_all or profile.status == 'gm':
        return render(request, 'toponomikon/this_location.html', context)
    else:
        return redirect('home:dupa')
