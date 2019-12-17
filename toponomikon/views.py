from django.db.models import Prefetch
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
        known_directly = GeneralLocation.objects.filter(known_directly=profile)
        known_indirectly = GeneralLocation.objects.filter(known_indirectly=profile)
        gen_locs = (known_directly | known_indirectly).distinct()
        spec_locs = (profile.spec_locs_known_directly.all() | profile.spec_locs_known_indirectly.all()).distinct()

    gen_locs = gen_locs\
        .prefetch_related(Prefetch('specific_locations', queryset=spec_locs))\
        .select_related('main_image')

    context = {
        'page_title': 'Toponomikon',
        'gen_locs': gen_locs,
    }
    return render(request, 'toponomikon/toponomikon_main.html', context)


def toponomikon_general_location_view(request, gen_loc_id):
    profile = request.user.profile
    gen_loc = get_object_or_404(GeneralLocation, id=gen_loc_id)
    if profile.character_status == 'gm':
        spec_locs = SpecificLocation.objects.filter(general_location__id=gen_loc_id)
    else:
        known_directly = SpecificLocation.objects.filter(general_location__id=gen_loc_id, known_directly=profile)
        known_indirectly = SpecificLocation.objects.filter(general_location__id=gen_loc_id, known_indirectly=profile)
        spec_locs = (known_directly | known_indirectly).distinct()

    context = {
        'page_title': gen_loc.name,
        'gen_loc': gen_loc,
        'spec_locs': spec_locs
    }
    return render(request, 'toponomikon/toponomikon_general_location.html', context)

