from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Prefetch, Case, When, Value, IntegerField, F, Q
from django.shortcuts import render, redirect

from prosoponomikon.forms import CharacterManyGroupsEditFormSet, \
    CharacterGroupsEditFormSetHelper, CharacterSingleGroupEditFormSet
from prosoponomikon.models import Character, PlayerCharacter, NPCCharacter, \
    CharacterGroup
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
        players = PlayerCharacter.objects.all()
        npcs = NPCCharacter.objects.all()
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
        all_known = all_known.prefetch_related('known_directly',
                                               'known_indirectly')
        # all_known = all_known.prefetch_related(
        #     Prefetch('biography_packets', queryset=profile.authored_bio_packets.all())
        # )
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
            'characters__profile__user')
        ungrouped = Character.objects.exclude(
            character_groups__in=character_groups)
        ungrouped = ungrouped.prefetch_related('profile__user')
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
        all_known = all_known.prefetch_related('known_directly',
                                               'known_indirectly')
        
        character_groups = character_groups.prefetch_related(
            Prefetch('characters__profile__user', queryset=all_known),
            # 'characters__profile__user'
        )
        ungrouped = all_known.exclude(character_groups__in=character_groups)
        
    context = {
        'page_title': 'Prosoponomikon',
        'character_groups': character_groups.order_by(
            F('order_no').asc(nulls_last=True), F('name')),
        'ungrouped': ungrouped.select_related('profile'),
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
def prosoponomikon_character_view(request, character_name):
    profile = request.user.profile
    
    characters = Character.objects.select_related()
    if profile.status == 'gm':
        characters = characters.prefetch_related('biography_packets',
                                                 'dialogue_packets')
    else:
        known_bio_packets = (profile.biography_packets.all()
                             | profile.authored_bio_packets.all())
        characters = characters.prefetch_related(
            Prefetch('biography_packets', queryset=known_bio_packets))

    character = characters.filter(name=character_name).first()

    # INFORM FORM
    if request.method == 'POST':
        handle_inform_form(request)
    
    context = {
        'page_title': character.name,
        'character': character,
    }
    if profile in character.all_known() or profile.status == 'gm':
        return render(request, 'prosoponomikon/character.html', context)
    else:
        return redirect('home:dupa')


@login_required
def prosoponomikon_character_groups_edit_view(request, group_id=0):
    profile = request.user.profile
    characters = Character.objects.prefetch_related()
    char_groups = CharacterGroup.objects.filter(author=profile)
    char_groups = char_groups.prefetch_related(
        'characters',
        'default_knowledge_packets')
    
    if group_id:
        char_groups = char_groups.filter(id=group_id)
        FormSet = CharacterSingleGroupEditFormSet
    else:
        FormSet = CharacterManyGroupsEditFormSet
        
    if request.method == 'POST':
        formset = FormSet(request.POST, queryset=char_groups)
        if formset.is_valid():
            try:
                for form in formset:
                    if form.is_valid():
                        # Ignore empty extra-form
                        if form.cleaned_data == {}:
                            pass
                        # Existing groups modification/deletion
                        elif form.cleaned_data.get('id') is not None:
                            if form.cleaned_data.get('DELETE'):
                                obj = form.cleaned_data.get('id')
                                obj.delete()
                                messages.success(
                                    request, f"Usunięto grupę '{obj.name}'!")
                            else:
                                obj = form.save()
                                if form.has_changed():
                                    messages.success(
                                        request, f"Zmodyfikowano grupę '{obj.name}'!")
                        # New group
                        else:
                            obj = form.save()
                            obj.author = profile
                            obj.save()
                            obj.characters.set(form.cleaned_data['characters'])
                            messages.success(
                                request, f"Utworzono grupę '{obj.name}'!")
                            
                return redirect('prosoponomikon:main')
            
            except IntegrityError:
                messages.warning(request, "Nazwy grup muszą być unikalne!")
                return redirect('prosoponomikon:groups-modify')
        else:
            messages.warning(request, formset.errors)
            
    else:
        formset = FormSet(queryset=char_groups)
        if profile.status != 'gm':
            characters = characters.filter(
                Q(known_directly=profile) | Q(known_indirectly=profile)
            ).distinct()
            for form in formset:
                form.fields['characters'].queryset = characters

    # Move 'extra' form to top
    formset.forms = [formset.forms[-1]] + formset.forms[:-1]
    
    context = {
        'page_title': "Dodaj/Edytuj grupy postaci",
        'formset': formset,
        'formset_helper': CharacterGroupsEditFormSetHelper(status=profile.status),
    }
    return render(request, '_formset.html', context)
