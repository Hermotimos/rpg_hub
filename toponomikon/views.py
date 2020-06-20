from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch, Q, Case, When, Value, IntegerField
from django.shortcuts import render, redirect, get_object_or_404

from knowledge.models import KnowledgePacket
from rpg_project.utils import send_emails
from toponomikon.models import GeneralLocation, SpecificLocation, Location


@login_required
def toponomikon_main_view(request):
    profile = request.user.profile
    if profile.status == 'gm':
        locs_lvl_1 = Location.objects.filter(in_location=None)
        locs_lvl_2 = Location.objects.filter(~Q(in_location=None))
    else:
        known_directly = profile.locations_known_directly.filter(in_location=None)
        known_indirectly = profile.locations_known_indirectly.filter(in_location=None)
        locs_lvl_1 = (known_directly | known_indirectly)
        locs_lvl_2 = (
                profile.locations_known_directly.filter(~Q(in_location=None))
                | profile.locations_known_indirectly.filter(~Q(in_location=None))
        ).distinct()

    locs_lvl_1 = locs_lvl_1\
        .prefetch_related(Prefetch('locations', queryset=locs_lvl_2))\
        .select_related('main_image', 'location_type__default_img')\
        .distinct()
        # .annotate(known_only_indirectly=Case(
        #     When(
        #         Q(known_indirectly=profile) & ~Q(known_directly=profile),
        #         then=Value(1)
        #     ),
        #     default=Value(0),
        #     output_field=IntegerField()
        # ))

    context = {
        'page_title': 'Toponomikon',
        'locs_lvl_1': locs_lvl_1.distinct(),
    }

    # for gen_loc in GeneralLocation.objects.all():
    #     loc = Location.objects.create(
    #         name=gen_loc.name,
    #         description=gen_loc.description,
    #         main_image=gen_loc.main_image,
    #         # pictures=gen_loc.pictures,
    #         # knowledge_packets=gen_loc.knowledge_packets,
    #         location_type=gen_loc.location_type,
    #         in_location=None,
    #         # known_directly=gen_loc.known_directly,
    #         # known_indirectly=gen_loc.known_indirectly,
    #         sorting_name=None,
    #     )
    #     loc.pictures.set([o for o in gen_loc.pictures.all()])
    #     loc.knowledge_packets.set([o for o in gen_loc.knowledge_packets.all()])
    #     loc.known_directly.set([o for o in gen_loc.known_directly.all()])
    #     loc.known_indirectly.set([o for o in gen_loc.known_indirectly.all()])
    #
    # for spec_loc in SpecificLocation.objects.all():
    #     loc = Location.objects.create(
    #         name=spec_loc.name,
    #         description=spec_loc.description,
    #         main_image=spec_loc.main_image,
    #         # pictures=spec_loc.pictures,
    #         # knowledge_packets=spec_loc.knowledge_packets,
    #         location_type=spec_loc.location_type,
    #         # in_location=spec_loc.general_location,
    #         # known_directly=spec_loc.known_directly,
    #         # known_indirectly=spec_loc.known_indirectly,
    #         sorting_name=spec_loc.sorting_name,
    #     )
    #     loc.pictures.set([o for o in spec_loc.pictures.all()])
    #     loc.knowledge_packets.set([o for o in spec_loc.knowledge_packets.all()])
    #     loc.known_directly.set([o for o in spec_loc.known_directly.all()])
    #     loc.known_indirectly.set([o for o in spec_loc.known_indirectly.all()])
    #     loc.in_location = Location.objects.get(name=spec_loc.general_location.name)
    #     loc.save()

    return render(request, 'toponomikon/toponomikon_main.html', context)


#
# @login_required
# def toponomikon_general_location_view(request, gen_loc_id):
#     profile = request.user.profile
#     gen_loc = get_object_or_404(Location, id=gen_loc_id)
#
#     gen_loc_known_directly = gen_loc.known_directly.all()
#     gen_loc_known_indirectly = gen_loc.known_indirectly.all()
#     allowed = (gen_loc_known_directly | gen_loc_known_indirectly)
#
#     # TABS
#     if profile.status == 'gm':
#         spec_locs = gen_loc.locations.all()
#         kn_packets = gen_loc.knowledge_packets.all()
#         only_indirectly = False
#     else:
#         known_directly = gen_loc.locations.filter(known_directly=profile)
#         known_indirectly = gen_loc.locations.filter(known_indirectly=profile).exclude(id__in=known_directly)
#         spec_locs = (known_directly | known_indirectly)
#         kn_packets = gen_loc.knowledge_packets.filter(acquired_by=profile)
#         only_indirectly = True \
#             if profile in gen_loc_known_indirectly\
#             and profile not in gen_loc_known_directly \
#             else False
#
#     spec_locs = spec_locs\
#         .select_related('main_image')\
#         .distinct()\
#         .annotate(known_only_indirectly=Case(
#             When(
#                 Q(known_indirectly=profile) & ~Q(known_directly=profile),
#                 then=Value(1)),
#             default=Value(0),
#             output_field=IntegerField()
#         ))
#
#     # INFORM LOCATION
#     # dict(request.POST).items() == < QueryDict: {
#     #     'csrfmiddlewaretoken': ['KcoYDwb7r86Ll2SdQUNrDCKs...'],
#     #     '2': ['on'],
#     #     'location': ['']
#     # } >
#     if request.method == 'POST' and 'location' in request.POST:
#         data = dict(request.POST)
#         informed_ids = [k for k, v_list in data.items() if 'on' in v_list]
#         gen_loc.known_indirectly.add(*informed_ids)
#
#         send_emails(request, informed_ids, location=gen_loc)
#         if informed_ids:
#             messages.info(request, f'Poinformowano wybrane postacie!')
#
#     # INFORM KNOWLEDGE PACKETS
#     # dict(request.POST).items() == < QueryDict: {
#     #   'csrfmiddlewaretoken': ['42GqawP0aa5WOfpuTkKixYsROBaKSQng...'],
#     #   '2': ['on'],
#     #   'kn_packet': ['38']
#     # } >
#     elif request.method == 'POST' and 'kn_packet' in request.POST:
#         data = dict(request.POST)
#         informed_ids = [k for k, v_list in data.items() if 'on' in v_list]
#         kn_packet_id = data['kn_packet'][0]
#         kn_packet = KnowledgePacket.objects.get(id=kn_packet_id)
#         kn_packet.acquired_by.add(*informed_ids)
#
#         send_emails(request, informed_ids, kn_packet=kn_packet)
#         if informed_ids:
#             messages.info(request, f'Poinformowano wybrane postacie!')
#
#     context = {
#         # General
#         'page_title': gen_loc.name,
#         'gen_loc': gen_loc,
#         'only_indirectly': only_indirectly,
#         # Tabs
#         'kn_packets': kn_packets,
#         'spec_locs': spec_locs,
#         'pictures': gen_loc.pictures.all(),
#     }
#     if profile in allowed or profile.status == 'gm':
#         return render(request, 'toponomikon/general_location.html', context)
#     else:
#         return redirect('home:dupa')
#
#
#
# @login_required
# def toponomikon_specific_location_view(request, spec_loc_id):
#     profile = request.user.profile
#     spec_loc = get_object_or_404(Location, id=spec_loc_id)
#
#     spec_loc_known_directly = spec_loc.known_directly.all()
#     spec_loc_known_indirectly = spec_loc.known_indirectly.all()
#     allowed = (spec_loc_known_directly | spec_loc_known_indirectly)
#
#     if profile.status == 'gm':
#         kn_packets = spec_loc.knowledge_packets.all()
#         only_indirectly = False
#     else:
#         kn_packets = spec_loc.knowledge_packets.filter(acquired_by=profile)
#         only_indirectly = True \
#             if profile in spec_loc_known_indirectly\
#             and profile not in spec_loc_known_directly \
#             else False
#
#     # INFORM LOCATION
#     # dict(request.POST).items() == < QueryDict: {
#     #     'csrfmiddlewaretoken': ['KcoYDwb7r86Ll2SdQUNrDCKs...'],
#     #     '2': ['on'],
#     #     'location': ['']
#     # } >
#     if request.method == 'POST' and 'location' in request.POST:
#         data = dict(request.POST)
#         informed_ids = [k for k, v_list in data.items() if 'on' in v_list]
#         spec_loc.known_indirectly.add(*informed_ids)
#
#         send_emails(request, informed_ids, location=spec_loc)
#         if informed_ids:
#             messages.info(request, f'Poinformowano wybrane postacie!')
#
#     # INFORM KNOWLEDGE PACKETS
#     # dict(request.POST).items() == < QueryDict: {
#     #   'csrfmiddlewaretoken': ['42GqawP0aa5WOfpuTkKixYsROBaKSQng...'],
#     #   '2': ['on'],
#     #   'kn_packet': ['38']
#     # } >
#
#     elif request.method == 'POST' and 'kn_packet' in request.POST:
#         data = dict(request.POST)
#         informed_ids = [k for k, v_list in data.items() if 'on' in v_list]
#         kn_packet_id = data['kn_packet'][0]
#         kn_packet = KnowledgePacket.objects.get(id=kn_packet_id)
#         kn_packet.acquired_by.add(*informed_ids)
#
#         send_emails(request, informed_ids, kn_packet=kn_packet)
#         if informed_ids:
#             messages.info(request, f'Poinformowano wybrane postacie!')
#
#     context = {
#         # General
#         'page_title': spec_loc.name,
#         'spec_loc': spec_loc,
#         'only_indirectly': only_indirectly,
#         # Tabs
#         'kn_packets': kn_packets,
#         'pictures': spec_loc.pictures.all(),
#     }
#     if profile in allowed or profile.status == 'gm':
#         return render(request, 'toponomikon/specific_location.html', context)
#     else:
#         return redirect('home:dupa')


@login_required
def toponomikon_location_view(request, loc_name):
    profile = request.user.profile
    location = get_object_or_404(Location, name=loc_name)
    
    known_directly_to = location.known_directly.all()
    known_indirectly_to = location.known_indirectly.all()
    allowed = (known_directly_to | known_indirectly_to)
    
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
    
    locations = locations \
        .select_related('main_image') \
        .distinct() \
        .annotate(known_only_indirectly=Case(
            When(
                Q(known_indirectly=profile) & ~Q(known_directly=profile),
                then=Value(1)
            ),
            default=Value(0),
            output_field=IntegerField(),
        ))
    
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
            messages.info(request, f'Poinformowano wybrane postacie!')
    
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
            messages.info(request, f'Poinformowano wybrane postacie!')

    page_title = location.name + ' (znasz z opowieści)' \
        if profile not in location.known_directly.all() and profile.status != 'gm'\
        else location.name
    
    context = {
        # General
        'page_title': page_title,
        'location': location,
        # Tabs
        'kn_packets': kn_packets,
        'locations': locations,
        'pictures': location.pictures.all(),
    }
    if profile in allowed or profile.status == 'gm':
        return render(request, 'toponomikon/this_location.html', context)
    else:
        return redirect('home:dupa')
