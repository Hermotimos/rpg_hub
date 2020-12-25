from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch, Q
from django.shortcuts import render, redirect, get_object_or_404

from prosoponomikon.models import PlayerCharacter, NonPlayerCharacter


@login_required
def prosoponomikon_main_view(request):
    profile = request.user.profile
    if profile.status == 'gm':
        player_characters = PlayerCharacter.objects.all()
        npc_characters = NonPlayerCharacter.objects.all()
    else:
        player_characters = []
        npc_characters = []
        
    context = {
        'page_title': 'Prosoponomikon',
        'player_characters': player_characters.select_related('profile'),
        'npc_characters': npc_characters.select_related('profile'),
    }
    return render(request, 'prosoponomikon/propoponomikon_main.html', context)


@login_required
def prosopa_view(request):
    profile = request.user.profile
    if profile.status == 'gm':
        player_characters = PlayerCharacter.objects.all()
        npc_characters = NonPlayerCharacter.objects.all()
    else:
        player_characters = []
        npc_characters = []
    
    context = {
        'page_title': 'Prosoponomikon',
        'player_characters': player_characters.select_related('profile'),
        'npc_characters': npc_characters.select_related('profile'),
    }
    return render(request, 'prosoponomikon/prosopa.html', context)
