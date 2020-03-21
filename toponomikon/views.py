from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db.models import Prefetch, Q, Case, When, Value, IntegerField
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, redirect, get_object_or_404

from rpg_project import settings
from rpg_project.utils import query_debugger
from toponomikon.forms import GeneralLocationInformForm, SpecificLocationInformForm
from toponomikon.models import GeneralLocation, SpecificLocation


@query_debugger
@login_required
def toponomikon_main_view(request):
    profile = request.user.profile
    if profile.character_status == 'gm':
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

    if profile.character_status == 'gm':
        spec_locs = SpecificLocation.objects.filter(general_location__id=gen_loc_id)
        knowledge_packets = gen_loc.knowledge_packets.all()
        is_gen_loc_known_only_indirectly = False
    else:
        known_directly = gen_loc.specific_locations.filter(known_directly=profile)
        known_indirectly = gen_loc.specific_locations.filter(known_indirectly=profile).exclude(id__in=known_directly)
        spec_locs = (known_directly | known_indirectly)
        knowledge_packets = gen_loc.knowledge_packets.filter(characters=profile.character)
        is_gen_loc_known_only_indirectly = \
            True if profile in gen_loc.known_indirectly.all() and profile not in gen_loc.known_directly.all() else False

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

    context = {
        'page_title': gen_loc.name,
        'gen_loc': gen_loc,
        'is_gen_loc_known_only_indirectly': is_gen_loc_known_only_indirectly,
        'knowledge_packets': knowledge_packets,
        'spec_locs': spec_locs,
        'pictures': None,
    }
    if profile in (gen_loc.known_directly.all() | gen_loc.known_indirectly.all()) or profile.character_status == 'gm':
        return render(request, 'toponomikon/toponomikon_general_location.html', context)
    else:
        return redirect('home:dupa')


@query_debugger
@login_required
def toponomikon_specific_location_view(request, spec_loc_id):
    profile = request.user.profile
    spec_loc = get_object_or_404(SpecificLocation, id=spec_loc_id)

    if profile.character_status == 'gm':
        is_spec_loc_known_only_indirectly = False
        knowledge_packets = spec_loc.knowledge_packets.all()
    else:
        is_spec_loc_known_only_indirectly = \
            True if profile in spec_loc.known_indirectly.all() and profile not in spec_loc.known_directly.all() \
            else False
        knowledge_packets = spec_loc.knowledge_packets.filter(characters=profile.character)

    context = {
        'page_title': spec_loc.name,
        'spec_loc': spec_loc,
        'is_spec_loc_known_only_indirectly': is_spec_loc_known_only_indirectly,
        'knowledge_packets': knowledge_packets,
        'pictures': None,
    }
    if profile in (spec_loc.known_directly.all() | spec_loc.known_indirectly.all()) or profile.character_status == 'gm':
        return render(request, 'toponomikon/toponomikon_specific_location.html', context)
    else:
        return redirect('home:dupa')


@query_debugger
@login_required
def toponomikon_inform_view(request, gen_loc_id='0', spec_loc_id='0'):
    profile = request.user.profile
    if gen_loc_id != 0:
        obj = get_object_or_404(GeneralLocation, id=gen_loc_id)
    else:
        obj = get_object_or_404(SpecificLocation, id=spec_loc_id)

    known_directly_old = obj.known_directly.all()
    known_indirectly_old = obj.known_indirectly.all()

    if request.method == 'POST':
        if isinstance(obj, GeneralLocation):
            form = GeneralLocationInformForm(authenticated_user=request.user,
                                             known_directly_old=known_directly_old,
                                             known_indirectly_old=known_indirectly_old,
                                             data=request.POST,
                                             instance=obj)
        else:
            form = SpecificLocationInformForm(authenticated_user=request.user,
                                              known_directly_old=known_directly_old,
                                              known_indirectly_old=known_indirectly_old,
                                              data=request.POST,
                                              instance=obj)

        if form.is_valid():
            known_indirectly_new = form.cleaned_data['known_indirectly']
            obj.known_indirectly.add(*list(known_indirectly_new))

            subject = f"[RPG] {profile} opowiedział Ci o pewnym miejscu!"
            message = f"{profile} opowiedział Ci o miejscu zwanym: {obj.name}.\n" \
                      f"Informacje zostały zapisane w Twoim Toponomikonie."
            sender = settings.EMAIL_HOST_USER
            receivers = []
            for new_profile in known_indirectly_new:
                receivers.append(new_profile.user.email)
            if profile.character_status != 'gm':
                receivers.append('lukas.kozicki@gmail.com')
            send_mail(subject, message, sender, receivers)

            messages.info(request, f'Poinformowałeś wybrane postacie!')
            _next = request.POST.get('next', '/')
            return HttpResponseRedirect(_next)
    else:
        if isinstance(obj, GeneralLocation):
            form = GeneralLocationInformForm(authenticated_user=request.user,
                                             known_directly_old=known_directly_old,
                                             known_indirectly_old=known_indirectly_old)
        else:
            form = SpecificLocationInformForm(authenticated_user=request.user,
                                              known_directly_old=known_directly_old,
                                              known_indirectly_old=known_indirectly_old)

    context = {
        'page_title': 'Opowiedz o krainie lub lokacji',
        'form': form,
        'obj': obj,
    }
    if profile in (obj.known_directly.all() | obj.known_indirectly.all()) or profile.character_status == 'gm':
        return render(request, 'toponomikon/toponomikon_inform.html', context)
    else:
        return redirect('home:dupa')
