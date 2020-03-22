from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch, Q
from django.shortcuts import render, redirect, get_object_or_404

from rpg_project.utils import query_debugger
from users.models import Profile


@query_debugger
@login_required
def prosoponomikon_main_view(request):
    players_profiles = Profile.objects.exclude(Q(status='living_npc') |
                                               Q(status='dead_npc') |
                                               Q(status='gm'))
    living_npc_profiles = Profile.objects.filter(status='living_npc')
    dead_npc_profiles = Profile.objects.filter(status='dead_npc')

    context = {
        'page_title': 'Prosoponomikon',
        'players_profiles': players_profiles,
        'living_npc_profiles': living_npc_profiles,
        'dead_npc_profiles': dead_npc_profiles,
    }
    return render(request, 'prosoponomikon/propoponomikon_main.html', context)
