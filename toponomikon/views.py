from django.db.models import Count, Prefetch, Q, Case, When, Value, IntegerField
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from rpg_project.utils import query_debugger
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
        .prefetch_related(Prefetch('specific_locations', queryset=spec_locs))\
        .select_related('main_image')\
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
        gen_loc_known_only_indirectly = False
    else:
        known_directly = gen_loc.specific_locations.filter(known_directly=profile)
        known_indirectly = gen_loc.specific_locations.filter(known_indirectly=profile).exclude(id__in=known_directly)
        spec_locs = (known_directly | known_indirectly)
        gen_loc_known_only_indirectly = \
            True if profile in gen_loc.known_indirectly.all() and not profile in gen_loc.known_directly.all() else False

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
        'gen_loc_known_only_indirectly': gen_loc_known_only_indirectly,
        'spec_locs': spec_locs
    }
    return render(request, 'toponomikon/toponomikon_general_location.html', context)

