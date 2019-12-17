from django.db.models import Prefetch
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

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


