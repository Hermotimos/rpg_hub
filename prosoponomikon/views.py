from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch, Q, Case, When, Value, IntegerField
from django.shortcuts import render, redirect, get_object_or_404

from prosoponomikon.forms import GMCharacterGroupCreateForm, CharacterGroupCreateForm
from prosoponomikon.models import PlayerCharacter, NonPlayerCharacter, CharacterGroup, Character


@login_required
def prosoponomikon_main_view(request):
    profile = request.user.profile
    if profile.character_groups_authored.all():
        return redirect('prosoponomikon:characters-grouped')
    else:
        return redirect('prosoponomikon:characters-ungrouped')


@login_required
def prosoponomikon_characters_ungrouped_view(request):
    profile = request.user.profile
    if profile.status == 'gm':
        players = PlayerCharacter.objects.all()
        npcs = NonPlayerCharacter.objects.all()
    else:
        known_dir = profile.characters_known_directly.all()
        known_indir = profile.characters_known_indirectly.all()
        known_only_indir = known_indir.exclude(id__in=known_dir)
        
        all_known = (known_dir | known_indir).distinct()
        all_known = all_known.annotate(
            only_indirectly=Case(
                When(id__in=known_only_indir, then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            ),
        )
        players = all_known.filter(profile__status__icontains='player')
        players = players.exclude(id=profile.character.id)
        npcs = all_known.exclude(profile__status__icontains='player')

    context = {
        'page_title': 'Prosoponomikon',
        'players': players.select_related('profile'),
        'npcs': npcs.select_related('profile'),
    }
    return render(request, 'prosoponomikon/characters_ungrouped.html', context)


@login_required
def prosoponomikon_characters_grouped_view(request):
    profile = request.user.profile
    character_groups = CharacterGroup.objects.filter(author=profile)
    
    if profile.status == 'gm':
        ungrouped = Character.objects.exclude(
            character_groups__in=character_groups)
    else:
        known_dir = profile.characters_known_directly.all()
        known_indir = profile.characters_known_indirectly.all()
        known_only_indir = known_indir.exclude(id__in=known_dir)
    
        all_known = (known_dir | known_indir).distinct()
        all_known = all_known.annotate(
            only_indirectly=Case(
                When(id__in=known_only_indir, then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            ),
        )
        all_known = all_known.exclude(id=profile.character.id)
        
        character_groups = character_groups.prefetch_related(
            Prefetch('characters', queryset=all_known),
            'characters__profile',
        )
        ungrouped = all_known.exclude(character_groups__in=character_groups)
        
    context = {
        'page_title': 'Prosoponomikon',
        'character_groups': character_groups,
        'ungrouped': ungrouped.prefetch_related('profile'),
    }
    if character_groups:
        return render(request, 'prosoponomikon/characters_grouped.html', context)
    else:
        return redirect('prosoponomikon:characters-ungrouped')


@login_required
def prosoponomikon_prosopa_view(request):
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


@login_required
def prosoponomikon_character_group_create_view(request):
    profile = request.user.profile
    if profile.status == 'gm':
        form = GMCharacterGroupCreateForm(data=request.POST or None)
    else:
        form = CharacterGroupCreateForm(data=request.POST or None)
    
    if form.is_valid():
        character_group = form.save(commit=False)
        character_group.author = profile
        character_group.save()
        character_group.characters.set(form.cleaned_data['characters'])
        messages.success(request, f"Utworzono grupę '{character_group.name}'!")
        return redirect('prosoponomikon:characters-grouped')
    else:
        messages.warning(request, form.errors)
    
    context = {
        'page_title': 'Nowa grupa',
        'form': form,
    }
    return render(request, '_form.html', context)
