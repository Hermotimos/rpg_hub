from django.shortcuts import render

from toponomikon.models import GeneralLocation, SpecificLocation
from users.models import Profile


def toponomikon_main_view(request):
    profile = request.user.profile
    if profile.character_status == 'gm':
        gen_locs = GeneralLocation.objects.all().prefetch_related('specific_locations')
    else:
        gen_locs_known_directly = Profile.gen_locs_known_directly.all().prefetch_related('specific_locations')
        gen_locs_known_indirectly = Profile.gen_locs_known_indirectly.all().prefetch_related('specific_locations')
        gen_locs = gen_locs_known_directly | gen_locs_known_indirectly

    context = {
        'page_title': 'Toponomikon',
        'gen_locs': gen_locs,
    }
    return render(request, 'toponomikon/toponomikon_main.html', context)
