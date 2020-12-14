from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch, Q
from django.shortcuts import render, redirect, get_object_or_404

from users.models import Profile

# Przenieść to wszystko do users -> przemianować users na prosoponomikon. No przecież...


@login_required
def prosoponomikon_main_view(request):
    profile = request.user.profile
    if profile.status == 'gm':
        players_profiles = Profile.objects.exclude(Q(status='living_npc') |
                                                   Q(status='dead_npc') |
                                                   Q(status='gm'))
        living_npc_profiles = Profile.objects.filter(status='living_npc')
        dead_npc_profiles = Profile.objects.filter(status='dead_npc')
    else:
        players_profiles = []
        living_npc_profiles = []
        dead_npc_profiles = []

    context = {
        'page_title': 'Prosoponomikon',
        'players_profiles': players_profiles,
        'living_npc_profiles': living_npc_profiles,
        'dead_npc_profiles': dead_npc_profiles,
    }
    return render(request, 'prosoponomikon/propoponomikon_main.html', context)
