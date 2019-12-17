from django.shortcuts import render

from rpg_project.utils import query_debugger
from toponomikon.models import GeneralLocation, SpecificLocation


@query_debugger
def toponomikon_main_view(request):
    profile = request.user.profile
    if profile.character_status == 'gm':
        gen_locs = GeneralLocation.objects.all()
    else:
        known_directly = GeneralLocation.objects.filter(known_directly=profile)
        known_indirectly = GeneralLocation.objects.filter(known_indirectly=profile)
        gen_locs = (known_directly | known_indirectly).distinct()

    gen_locs = gen_locs.prefetch_related('specific_locations').select_related('main_image')

    context = {
        'page_title': 'Toponomikon',
        'gen_locs': gen_locs,
    }
    return render(request, 'toponomikon/toponomikon_main.html', context)
