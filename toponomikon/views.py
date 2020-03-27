from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db.models import Prefetch, Q, Case, When, Value, IntegerField
from django.shortcuts import render, redirect, get_object_or_404

from knowledge.models import KnowledgePacket
from rpg_project import settings
from rpg_project.utils import query_debugger
from toponomikon.models import GeneralLocation, SpecificLocation
from toponomikon.utils import (
    send_mails_inform_location,
    send_mails_inform_kn_packet,
)
from users.models import Profile


@query_debugger
@login_required
def toponomikon_main_view(request):
    profile = request.user.profile
    if profile.status == 'gm':
        gen_locs = GeneralLocation.objects.all()
        spec_locs = SpecificLocation.objects.all()
    else:
        known_directly = profile.gen_locs_known_directly.all()
        known_indirectly = profile.gen_locs_known_indirectly.exclude(id__in=known_directly)
        gen_locs = (known_directly | known_indirectly)
        spec_locs = (profile.spec_locs_known_directly.all() | profile.spec_locs_known_indirectly.all()).distinct()

    gen_locs = gen_locs\
        .prefetch_related(Prefetch('specific_locations', queryset=spec_locs),)\
        .select_related('main_image', 'location_type__default_img')\
        .distinct()\
        .annotate(known_only_indirectly=Case(
            When(
                Q(known_indirectly=profile) & ~Q(known_directly=profile),
                then=Value(1)
            ),
            default=Value(0),
            output_field=IntegerField()
        ))

    context = {
        'page_title': 'Toponomikon',
        'gen_locs': gen_locs,
    }
    return render(request, 'toponomikon/toponomikon_main.html', context)


@query_debugger
@login_required
def toponomikon_general_location_view(request, gen_loc_id):
    profile = request.user.profile
    gen_loc = get_object_or_404(GeneralLocation, id=gen_loc_id)
    
    gen_loc_known_directly = gen_loc.known_directly.all()
    gen_loc_known_indirectly = gen_loc.known_indirectly.all()
    allowed = (gen_loc_known_directly | gen_loc_known_indirectly)

    # TABS
    if profile.status == 'gm':
        spec_locs = gen_loc.specific_locations.all()
        knowledge_packets = gen_loc.knowledge_packets.all()
        only_indirectly = False
    else:
        known_directly = gen_loc.specific_locations.filter(known_directly=profile)
        known_indirectly = gen_loc.specific_locations.filter(known_indirectly=profile).exclude(id__in=known_directly)
        spec_locs = (known_directly | known_indirectly)
        knowledge_packets = gen_loc.knowledge_packets.filter(acquired_by=profile)
        only_indirectly = True \
            if profile in gen_loc_known_indirectly\
            and profile not in gen_loc_known_directly \
            else False

    spec_locs = spec_locs\
        .select_related('main_image')\
        .distinct()\
        .annotate(known_only_indirectly=Case(
            When(
                Q(known_indirectly=profile) & ~Q(known_directly=profile),
                then=Value(1)),
            default=Value(0),
            output_field=IntegerField()
        ))
    
    # INFORM LOCATION
    if request.method == 'POST' and 'location' in request.POST:
        data = dict(request.POST)
        informed_ids = [k for k, v_list in data.items() if 'on' in v_list]
        # dict(request.POST).items() == < QueryDict: {
        #     'csrfmiddlewaretoken': ['KcoYDwb7r86Ll2SdQUNrDCKs...'],
        #     '2': ['on'],
        #     'location': ['']
        # } >
        gen_loc.known_indirectly.add(*informed_ids)
        
        send_mails_inform_location(request, gen_loc, informed_ids)
        messages.info(request, f'Poinformowano wybrane postacie!')

    # INFORM KNOWLEDGE PACKETS
    elif request.method == 'POST' and 'kn_packet' in request.POST:
        data = dict(request.POST)
        informed_ids = [k for k, v_list in data.items() if 'on' in v_list]
        # dict(request.POST).items() == < QueryDict: {
        #   'csrfmiddlewaretoken': ['42GqawP0aa5WOfpuTkKixYsROBaKSQng...'],
        #   '2': ['on'],
        #   'kn_packet': ['38']
        # } >
        kn_packet_id = data['kn_packet'][0]
        kn_packet = KnowledgePacket.objects.get(id=kn_packet_id)
        kn_packet.acquired_by.add(*informed_ids)

        send_mails_inform_kn_packet(request, kn_packet, informed_ids)
        messages.info(request, f'Poinformowano wybrane postacie!')

    context = {
        # General
        'page_title': gen_loc.name,
        'gen_loc': gen_loc,
        'only_indirectly': only_indirectly,
        # Tabs
        'knowledge_packets': knowledge_packets,
        'spec_locs': spec_locs,
        'pictures': gen_loc.pictures.all(),
        # Inform
        'informable': gen_loc.informable(),
    }
    if profile in allowed or profile.status == 'gm':
        return render(request, 'toponomikon/general_location.html', context)
    else:
        return redirect('home:dupa')


@query_debugger
@login_required
def toponomikon_specific_location_view(request, spec_loc_id):
    profile = request.user.profile
    spec_loc = get_object_or_404(SpecificLocation, id=spec_loc_id)
    
    spec_loc_known_directly = spec_loc.known_directly.all()
    spec_loc_known_indirectly = spec_loc.known_indirectly.all()
    allowed = (spec_loc_known_directly | spec_loc_known_indirectly)

    if profile.status == 'gm':
        knowledge_packets = spec_loc.knowledge_packets.all()
        only_indirectly = False
    else:
        knowledge_packets = spec_loc.knowledge_packets.filter(
            acquired_by=profile
        )
        only_indirectly = True \
            if profile in spec_loc_known_indirectly\
            and profile not in spec_loc_known_directly \
            else False

    # INFORM LOCATION
    if request.method == 'POST' and 'location' in request.POST:
        data = dict(request.POST)
        informed_ids = [id_ for id_, list_ in data.items() if 'on' in list_]
        # Following data is returned by dict(request.POST).items():
        # < QueryDict: {
        #     'csrfmiddlewaretoken': ['KcoYDwb7r86Ll2SdQUNrDCKs...'],
        #     '2': ['on'],
        #     'location': ['']
        # } >
        spec_loc.known_indirectly.add(*informed_ids)
    
        subject = f"[RPG] {profile} opowiedział Ci o pewnym miejscu!"
        message = f"{profile} opowiedział Ci o miejscu zwanym:" \
                  f" '{spec_loc.name}'.\n" \
                  f"Informacje zostały zapisane w Twoim Toponomikonie: " \
                  f"{request.build_absolute_uri()}"
        sender = settings.EMAIL_HOST_USER
        receivers = [
            p.user.email for p in Profile.objects.filter(id__in=informed_ids)
        ]
        if profile.status != 'gm':
            receivers.append('lukas.kozicki@gmail.com')
        send_mail(subject, message, sender, receivers)
        
        messages.info(request, f'Poinformowano wybrane postacie!')

    # INFORM KNOWLEDGE PACKETS
    elif request.method == 'POST' and 'kn_packet' in request.POST:
        data = dict(request.POST)
        informed_ids = [id_ for id_, list_ in data.items() if 'on' in list_]
        # < QueryDict: {
        #   'csrfmiddlewaretoken': ['42GqawP0aa5WOfpuTkKixYsROBaKSQng...'],
        #   '2': ['on'],
        #   'kn_packet': ['38']
        # } >
        kn_packet_id = data['kn_packet'][0]
        kn_packet = KnowledgePacket.objects.get(id=kn_packet_id)
        kn_packet.acquired_by.add(*informed_ids)
    
        subject = f"[RPG] Transfer wiedzy: '{kn_packet.title}'"
        message = f"{profile} przekazał Ci wiedzę: '{kn_packet.title}'.\n" \
                  f"Więdzę tę możesz odnaleźć pod umiejętnością/ami:" \
                  f" {', '.join(s.name for s in kn_packet.skills.all())}" \
                  f" w zakładce Almanach: " \
                  f"{request.get_host()}/knowledge/almanac/\n"
        sender = settings.EMAIL_HOST_USER
        receivers = [
            p.user.email for p in Profile.objects.filter(id__in=informed_ids)
        ]
        if profile.status != 'gm':
            receivers.append('lukas.kozicki@gmail.com')
        send_mail(subject, message, sender, receivers)
        
        messages.info(request, f'Poinformowano wybrane postacie!')

    context = {
        # General
        'page_title': spec_loc.name,
        'spec_loc': spec_loc,
        'only_indirectly': only_indirectly,
        # Tabs
        'knowledge_packets': knowledge_packets,
        'pictures': spec_loc.pictures.all(),
        # Inform
        'informable': spec_loc.informable(),
    }
    if profile in allowed or profile.status == 'gm':
        return render(request, 'toponomikon/specific_location.html', context)
    else:
        return redirect('home:dupa')
