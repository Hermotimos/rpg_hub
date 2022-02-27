from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Prefetch, Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect

from imaginarion.models import Picture, PictureImage, PictureSet
from knowledge.forms import BioPacketForm, PlayerBioPacketForm
from knowledge.models import BiographyPacket
from prosoponomikon.forms import CharacterManyGroupsEditFormSet, \
    CharacterGroupsEditFormSetHelper, CharacterGroupCreateForm, \
    CharacterCreateForm
from prosoponomikon.models import Character, CharacterGroup, NameGroup, \
    FamilyName
from rpg_project.settings import get_secret
from rpg_project.utils import handle_inform_form, backup_db, only_game_masters, \
    only_game_masters_and_spectators
from rules.utils import get_synergies_acquired
from toponomikon.models import Location
from users.models import Profile, User


@login_required
def prosoponomikon_ungrouped_view(request):
    profile = Profile.objects.get(id=request.session['profile_id'])
    all_characters = profile.characters_known_annotated()
    context = {
        'current_profile': profile,
        'page_title': 'Prosoponomikon',
        'all_characters': all_characters,
    }
    return render(request, 'prosoponomikon/characters_ungrouped.html', context)


@login_required
def prosoponomikon_grouped_view(request):
    profile = Profile.objects.get(id=request.session['profile_id'])
    
    character_groups = profile.characters_groups_authored_with_characters()
    all_characters = profile.characters_known_annotated()
    player_characters = all_characters.filter(profile__status="player")
    ungrouped_characters = all_characters.exclude(
        character_groups__in=character_groups).exclude(id__in=player_characters)
    
    context = {
        'current_profile': profile,
        'page_title': 'Prosoponomikon',
        'player_characters': player_characters,
        'character_groups': character_groups,
        'ungrouped_characters': ungrouped_characters,
    }
    return render(request, 'prosoponomikon/characters_grouped.html', context)


@login_required
def prosoponomikon_character_view(request, character_id):
    profile = Profile.objects.get(id=request.session['profile_id'])
    if profile.can_view_all:
        return redirect('prosoponomikon:character-for-gm', character_id)
    else:
        return redirect('prosoponomikon:character-for-player', character_id)


@login_required
@only_game_masters_and_spectators
def prosoponomikon_character_for_gm_view(request, character_id):
    profile = Profile.objects.get(id=request.session['profile_id'])
    if profile.character.id == character_id:
        character = profile.character
    else:
        character = Character.objects.get(id=character_id)

    known_characters = character.profile.characters_known_annotated()
    
    # NPCs: Default skills and kn_packets if Character in a CharacterGroup
    if character.profile.status == 'npc' and character.character_groups.exists():
        synergies = []
        skills = []
        knowledge_packets = []
        for character_group in character.character_groups.all():
            for skill in character_group.default_skills.all():
                skills.append(skill)
            for kn_packet in character_group.default_knowledge_packets.all():
                knowledge_packets.append(kn_packet)
                
    # Players: Own skills and kn_packets etc. of a Player
    else:
        skills = character.profile.skills_acquired_with_skill_levels()
        skills = skills.prefetch_related('skill_levels__perks__conditional_modifiers__conditions')
        skills = skills.prefetch_related('skill_levels__perks__conditional_modifiers__combat_types')
        skills = skills.prefetch_related('skill_levels__perks__conditional_modifiers__modifier__factor')
        skills = skills.prefetch_related('skill_levels__perks__comments')
        skills = skills.distinct()

        synergies = get_synergies_acquired(character.profile)
        
        knowledge_packets = character.profile.knowledge_packets.order_by('title')
        knowledge_packets = knowledge_packets.prefetch_related('picture_sets__pictures')
 
    # INFORM FORM
    if request.method == 'POST':
        handle_inform_form(request)
    
    context = {
        'current_profile': profile,
        'page_title': character,
        'character': character,
        'skills': skills,
        'synergies': synergies,
        'known_characters': known_characters,
        'knowledge_packets': knowledge_packets,
    }
    return render(request, 'prosoponomikon/character.html', context)


@login_required
def prosoponomikon_character_for_player_view(request, character_id):
    profile = Profile.objects.get(id=request.session['profile_id'])
    
    known_bio_packets = (
        profile.biography_packets.all() | profile.authored_bio_packets.all())
    characters = Character.objects.select_related('first_name')
    characters = characters.prefetch_related(
        Prefetch('biography_packets', queryset=known_bio_packets))
    
    character = characters.filter(id=character_id).first()
    
    # Player viewing own Character
    if profile.character.id == character_id:
        skills = profile.skills_acquired_with_skill_levels()
        skills = skills.prefetch_related('skill_levels__perks__conditional_modifiers__conditions')
        skills = skills.prefetch_related('skill_levels__perks__conditional_modifiers__combat_types')
        skills = skills.prefetch_related('skill_levels__perks__conditional_modifiers__modifier__factor')
        skills = skills.prefetch_related('skill_levels__perks__comments')
        skills = skills.distinct()
        
        synergies = get_synergies_acquired(profile)

        knowledge_packets = profile.knowledge_packets.order_by('title')
        knowledge_packets = knowledge_packets.prefetch_related('picture_sets__pictures')
        known_characters = character.profile.characters_known_annotated()
    
    # Player viewing other Characters
    else:
        skills, knowledge_packets, known_characters, synergies = [], [], [], []

    # INFORM FORM
    if request.method == 'POST':
        handle_inform_form(request)
    
    context = {
        'current_profile': profile,
        'page_title': character,
        'character': character,
        'skills': skills,
        'synergies': synergies,
        'knowledge_packets': knowledge_packets,
        'known_characters': known_characters,
    }
    if (profile in character.all_known() or profile.character == character
            or profile.can_view_all):
        return render(request, 'prosoponomikon/character.html', context)
    else:
        return redirect('users:dupa')


@login_required
def prosoponomikon_character_groups_edit_view(request):
    current_profile = Profile.objects.get(id=request.session['profile_id'])
    characters = Character.objects.prefetch_related()
    char_groups = CharacterGroup.objects.filter(author=current_profile)
    char_groups = char_groups.prefetch_related(
        'characters', 'default_knowledge_packets')
        
    if request.method == 'POST':
        formset = CharacterManyGroupsEditFormSet(request.POST)
        if formset.is_valid():
            try:
                formset.save()
                any_changed = False
                
                for form in formset:
                    if form.is_valid():
                        # Deletion
                        if form.cleaned_data.get('DELETE'):
                            obj = form.cleaned_data.get('id')
                            obj.delete()
                            any_changed = True
                            messages.success(request, f"Usunięto grupę '{obj.name}'!")
                        # Modification
                        else:
                            obj = form.save()
                            obj.save()
                            if form.has_changed():
                                any_changed = True
                                messages.success(request, f"Zmodyfikowano grupę '{obj.name}'!")
                    # form invalid
                    else:
                        messages.warning(request, form.errors)
                        return redirect('prosoponomikon:groups-edit')
                
                if not any_changed:
                    messages.warning(request, "Nie dokonano żadnych zmian!")
                    
                return redirect('prosoponomikon:grouped')

            except IntegrityError:
                messages.warning(request, "Nazwy grup muszą być unikalne!")
                return redirect('prosoponomikon:groups-edit')
            
        # formset invalid
        else:
            messages.warning(request, formset.errors)
            
    else:
        formset = CharacterManyGroupsEditFormSet(queryset=char_groups)
        if current_profile.status != 'gm':
            characters = characters.filter(
                Q(known_directly=current_profile)
                | Q(known_indirectly=current_profile)
            ).distinct()
            for form in formset:
                form.fields['characters'].queryset = characters
    
    context = {
        'current_profile': current_profile,
        'page_title': "Edytuj grupy Postaci",
        'formset': formset,
        'formset_helper': CharacterGroupsEditFormSetHelper(
            status=current_profile.status),
    }
    return render(request, '_formset.html', context)


@login_required
def prosoponomikon_character_group_create_view(request):
    profile = Profile.objects.get(id=request.session['profile_id'])
    form = CharacterGroupCreateForm(data=request.POST or None, profile=profile)
    
    if form.is_valid():
        character_group = form.save()
        character_group.author = profile
        character_group.save()
        messages.success(
            request, f'Utworzono grupę Postaci "{character_group.name}"!')
        return redirect('prosoponomikon:grouped')
    else:
        messages.warning(request, form.errors)
        
    context = {
        'current_profile': profile,
        'page_title': "Nowa grupa Postaci",
        'form': form,
    }
    return render(request, '_form.html', context)

    
@login_required
def prosoponomikon_bio_packet_form_view(request, bio_packet_id=0, character_id=0):
    profile = Profile.objects.get(id=request.session['profile_id'])

    bio_packet = BiographyPacket.objects.filter(id=bio_packet_id).first()
    character = Character.objects.filter(id=character_id).first()

    if profile.status == 'gm':
        form = BioPacketForm(data=request.POST or None,
                             files=request.FILES or None,
                             instance=bio_packet)
    else:
        form = PlayerBioPacketForm(data=request.POST or None,
                                   files=request.FILES or None,
                                   instance=bio_packet)
    
    if form.is_valid():
        if profile.status == 'gm':
            bio_packet = form.save()
        else:
            bio_packet = form.save(commit=False)
            bio_packet.author = profile
            bio_packet.save()
            bio_packet.acquired_by.add(profile)
            
            pictures = [v for k, v in form.cleaned_data.items()
                        if 'picture' in k and v is not None]

            new_pictures = []
            for cnt, picture in enumerate(pictures, 1):
                description = (form.cleaned_data[f'descr_{cnt}']
                               or f"{bio_packet.title}")
                pic_img = PictureImage.objects.create(
                    image=picture,
                    description=description)
                pic = Picture.objects.create(
                    image=pic_img,
                    type='players-notes',
                    description=description)
                new_pictures.append(pic)

            if new_pictures:
                now = datetime.now().strftime("%Y-%d-%m %H:%M:%S")
                title = f"""
                    BiographyPacket: '{bio_packet.title}'
                    [Autor: {profile.character.first_name} - {now}]
                """
                new_picture_set = PictureSet.objects.create(title=title)
                new_picture_set.pictures.set(new_pictures)
                bio_packet.picture_sets.add(new_picture_set)

        character.biography_packets.add(bio_packet)
        
        messages.success(request, "Zapisano pakiet biograficzny!")
        return redirect('prosoponomikon:character', character_id)

    else:
        messages.warning(request, form.errors)

    context = {
        'current_profile': profile,
        'page_title': f"{character}: " + (
            bio_packet.title if bio_packet else 'Nowy pakiet wiedzy'),
        'form': form,
    }
    if not bio_packet_id or profile.status == 'gm' \
            or profile.biography_packets.filter(id=bio_packet_id):
        return render(request, '_form.html', context)
    else:
        return redirect('users:dupa')


@login_required
@only_game_masters
def prosoponomikon_first_names_view(request):
    profile = Profile.objects.get(id=request.session['profile_id'])
    
    name_groups = NameGroup.objects.prefetch_related(
        'affix_groups__first_names__characters__profile',
        'affix_groups__first_names__auxiliary_group__location',
    )
    context = {
        'current_profile': profile,
        'page_title': "Imiona",
        'name_groups': name_groups,
    }
    return render(request, 'prosoponomikon/first_names.html', context)


@login_required
@only_game_masters
def prosoponomikon_family_names_view(request):
    profile = Profile.objects.get(id=request.session['profile_id'])
    
    family_names = FamilyName.objects.select_related('group')
    family_names = family_names.prefetch_related(
        'characters__profile', 'locations')

    context = {
        'current_profile': profile,
        'page_title': "Nazwiska",
        'family_names': family_names,
    }
    return render(request, 'prosoponomikon/family_names.html', context)


@login_required
@only_game_masters
def prosoponomikon_character_create_form_view(request):
    """Handle CharacterCreateForm intended for GM."""
    profile = Profile.objects.get(id=request.session['profile_id'])
    
    form = CharacterCreateForm(
        data=request.POST or None, files=request.FILES or None)
    
    if form.is_valid():
        character = form.save(commit=False)
    
        user = User.objects.create_user(
            username=form.cleaned_data['username'],
            password=get_secret('DEFAULT_PASS'))
        
        profile = Profile.objects.create(
            user=user,
            is_alive=form.cleaned_data['is_alive'],
            image=form.cleaned_data['image'])
        
        character.profile = profile
        form.save()

        messages.success(request, f"Utworzono Postać {character}!")
        return redirect('prosoponomikon:character-create')
        
    context = {
        'current_profile': profile,
        'page_title': "Nowa Postać",
        'form': form,
    }
    return render(request, '_form.html', context)


@login_required
@only_game_masters
def prosoponomikon_acquaintances_view(request, location_id):
    """Make everybody know directly everybody in a given Location."""
    location = Location.objects.get(id=location_id)
    backup_db(reason=f"acquaintances_{location.name}")
    
    inhabitants = Character.objects.filter(
        frequented_locations__in=location.with_sublocations()).distinct()

    for character in inhabitants:
        [character.known_directly.add(i.profile) for i in inhabitants]

    msg = f"""
        {location.name}:
        zapoznano ze sobą wszystkie Postacie [{len(inhabitants)}]!
    """
    messages.success(request, msg)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
