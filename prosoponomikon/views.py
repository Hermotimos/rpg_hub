from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch, Case, When, Value, IntegerField
from django.shortcuts import render, redirect

from prosoponomikon.forms import CharacterGroupCreateForm, GMCharcterGroupCreateForm
from prosoponomikon.models import Character, PlayerCharacter, NPCCharacter, CharacterGroup
from rpg_project.utils import handle_inform_form
from users.models import Profile


@login_required
def prosoponomikon_main_view(request):
    profile = request.user.profile
    if profile.character_groups_authored.all():
        return redirect('prosoponomikon:grouped')
    else:
        return redirect('prosoponomikon:ungrouped')


@login_required
def prosoponomikon_ungrouped_view(request):
    profile = request.user.profile
    if profile.status == 'gm':
        players = PlayerCharacter.objects.prefetch_related('biography_packets')
        npcs = NPCCharacter.objects.prefetch_related('biography_packets')
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
        all_known = all_known.prefetch_related(
            Prefetch('biography_packets', queryset=profile.authored_bio_packets.all())
        )
        players = all_known.filter(profile__in=Profile.players.all())
        players = players.exclude(id=profile.character.id)
        npcs = all_known.filter(profile__in=Profile.npcs.all())

    context = {
        'page_title': 'Prosoponomikon',
        'players': players.select_related('profile'),
        'npcs': npcs.select_related('profile'),
    }
    return render(request, 'prosoponomikon/characters_ungrouped.html', context)


@login_required
def prosoponomikon_grouped_view(request):
    profile = request.user.profile
    character_groups = CharacterGroup.objects.filter(author=profile)
    
    if profile.status == 'gm':
        character_groups = character_groups.prefetch_related(
            'characterss__biography_packets')
        ungrouped = Character.objects.exclude(
            character_groups__in=character_groups)
        ungrouped = ungrouped.prefetch_related('biography_packets')
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
        all_known = all_known.prefetch_related(
            Prefetch('biography_packets', queryset=profile.authored_bio_packets.all())
        )
        
        character_groups = character_groups.prefetch_related(
            Prefetch('characters', queryset=all_known),
            'characters__profile',
        )
        ungrouped = all_known.exclude(character_groups=character_groups)
        
    context = {
        'page_title': 'Prosoponomikon',
        'character_groups': character_groups,
        'ungrouped': ungrouped.prefetch_related('profile'),
    }
    if character_groups:
        return render(request, 'prosoponomikon/characters_grouped.html', context)
    else:
        return redirect('prosoponomikon:ungrouped')


# @login_required
# def prosoponomikon_characters_view(request):
#     profile = request.user.profile
#     if profile.status == 'gm':
#         player_characters = PlayerCharactera.objects.all()
#         npc_characters = NPCCharacter.objects.all()
#     else:
#         player_characters = []
#         npc_characters = []
#
#     context = {
#         'page_title': 'Prosoponomikon',
#         'player_character': player_characters.select_related('profile'),
#         'npc_characters': npc_characters.select_related('profile'),
#     }
#     return render(request, 'prosoponomikon/characters.html', context)


@login_required
def prosoponomikon_group_create_view(request):
    profile = request.user.profile
    if profile.status == 'gm':
        form = GMCharcterGroupCreateForm(data=request.POST or None)
    else:
        form = CharacterGroupCreateForm(data=request.POST or None)
    
    if form.is_valid():
        character_group = form.save(commit=False)
        character_group.author = profile
        character_group.save()
        character_group.characters.set(form.cleaned_data['characters'])
        messages.success(request, f"Utworzono grupę '{character_group.name}'!")
        return redirect('prosoponomikon:grouped')
    else:
        messages.warning(request, form.errors)
    
    context = {
        'page_title': 'Nowa grupa',
        'form': form,
    }
    return render(request, '_form.html', context)


@login_required
def prosoponomikon_character_view(request, character_name):
    profile = request.user.profile
    characters = Character.objects.select_related()
    if profile.status == 'gm':

        characters = characters.prefetch_related('biography_packets', 'dialogue_packets')
    else:
        # TODO analogicznie do Toponomikonu - wyfiltorwać kto co zna
        pass
    
    character = characters.get(name=character_name)

    # INFORM FORM
    if request.method == 'POST':
        handle_inform_form(request)
    
    context = {
        'page_title': character.name, # TODO (znasz ze słyszenia) if only indirectly
        'character': character,
    }
    return render(request, 'prosoponomikon/character_detail.html', context)
