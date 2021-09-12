from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Prefetch, Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect

from imaginarion.models import Picture, PictureImage
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
from toponomikon.models import Location
from users.models import Profile, User


@login_required
def prosoponomikon_ungrouped_view(request):
    profile = request.user.profile
    all_characters = profile.characters_all_known_annotated_if_indirectly()
    context = {
        'page_title': 'Prosoponomikon',
        'all_characters': all_characters,
    }
    return render(request, 'prosoponomikon/characters_ungrouped.html', context)


@login_required
def prosoponomikon_grouped_view(request):
    profile = request.user.profile
    
    character_groups = profile.characters_groups_authored_with_characters()
    all_characters = profile.characters_all_known_annotated_if_indirectly()
    player_characters = all_characters.filter(profile__status="player")
    ungrouped_characters = all_characters.exclude(
        character_groups__in=character_groups).exclude(id__in=player_characters)
    
    context = {
        'page_title': 'Prosoponomikon',
        'player_characters': player_characters,
        'character_groups': character_groups,
        'ungrouped_characters': ungrouped_characters,
    }
    return render(request, 'prosoponomikon/characters_grouped.html', context)


@login_required
def prosoponomikon_character_view(request, character_id):
    profile = request.user.profile
    if profile.can_view_all:
        return redirect('prosoponomikon:character-for-gm', character_id)
    else:
        return redirect('prosoponomikon:character-for-player', character_id)


@login_required
@only_game_masters_and_spectators
def prosoponomikon_character_for_gm_view(request, character_id):
    profile = request.user.profile
    if profile.character.id == character_id:
        character = profile.character
    else:
        character = Character.objects.get(id=character_id)

    known_characters = character.profile.characters_all_known_annotated_if_indirectly()
    
    # NPCs: Default skills and kn_packets etc. as per CharacterGroup
    if character.profile.status == 'npc':
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
        knowledge_packets = character.profile.knowledge_packets.order_by('title')
        knowledge_packets = knowledge_packets.prefetch_related('pictures')
 
    # INFORM FORM
    if request.method == 'POST':
        handle_inform_form(request)
    
    context = {
        'page_title': character,
        'character': character,
        'skills': skills,
        'known_characters': known_characters,
        'knowledge_packets': knowledge_packets,
    }
    return render(request, 'prosoponomikon/character.html', context)


@login_required
def prosoponomikon_character_for_player_view(request, character_id):
    profile = request.user.profile
    
    known_bio_packets = (
        profile.biography_packets.all() | profile.authored_bio_packets.all())
    characters = Character.objects.select_related('first_name')
    characters = characters.prefetch_related(
        Prefetch('biography_packets', queryset=known_bio_packets))
    
    character = characters.filter(id=character_id).first()
    
    # Player viewing own Character
    if profile.character.id == character_id:
        skills = profile.skills_acquired_with_skill_levels()
        knowledge_packets = profile.knowledge_packets.order_by('title')
        knowledge_packets = knowledge_packets.prefetch_related('pictures')
        known_characters = character.profile.characters_all_known_annotated_if_indirectly()
    
    # Player viewing other Characters
    else:
        skills, knowledge_packets, known_characters = [], [], []

    # INFORM FORM
    if request.method == 'POST':
        handle_inform_form(request)
    
    context = {
        'page_title': character,
        'character': character,
        'skills': skills,
        'knowledge_packets': knowledge_packets,
        'known_characters': known_characters,
    }
    if (profile in character.all_known() or profile.character == character
            or profile.can_view_all):
        return render(request, 'prosoponomikon/character.html', context)
    else:
        return redirect('home:dupa')


@login_required
def prosoponomikon_character_groups_edit_view(request):
    profile = request.user.profile
    characters = Character.objects.prefetch_related()
    char_groups = CharacterGroup.objects.filter(author=profile)
    char_groups = char_groups.prefetch_related(
        'characters',
        'default_knowledge_packets')
        
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
                            messages.success(
                                request, f"Usunięto grupę '{obj.name}'!")
                        # Modification
                        else:
                            obj = form.save()
                            obj.save()
                            if form.has_changed():
                                any_changed = True
                                messages.success(
                                    request,  f"Zmodyfikowano grupę '{obj.name}'!")
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
        if profile.status != 'gm':
            characters = characters.filter(
                Q(known_directly=profile) | Q(known_indirectly=profile)
            ).distinct()
            for form in formset:
                form.fields['characters'].queryset = characters
    
    context = {
        'page_title': "Edytuj grupy postaci",
        'formset': formset,
        'formset_helper': CharacterGroupsEditFormSetHelper(status=profile.status),
    }
    return render(request, '_formset.html', context)


@login_required
def prosoponomikon_character_group_create_view(request):
    profile = request.user.profile
    form = CharacterGroupCreateForm(data=request.POST or None, profile=profile)
    
    if form.is_valid():
        character_group = form.save()
        character_group.author = profile
        character_group.save()
        messages.success(
            request, f'Utworzono grupę postaci "{character_group.name}"!')
        return redirect('prosoponomikon:grouped')
    else:
        messages.warning(request, form.errors)
        
    context = {
        'page_title': "Nowa grupa postaci",
        'form': form,
    }
    return render(request, '_form.html', context)

    
@login_required
def prosoponomikon_bio_packet_form_view(request, bio_packet_id=0, character_id=0):
    profile = request.user.profile

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
                bio_packet.pictures.add(pic)

        character.biography_packets.add(bio_packet)
        
        messages.success(request, "Zapisano pakiet biograficzny!")
        return redirect('prosoponomikon:character', character_id)

    else:
        messages.warning(request, form.errors)

    context = {
        'page_title': f"{character}: " + (
            bio_packet.title if bio_packet else 'Nowy pakiet wiedzy'),
        'form': form,
    }
    if not bio_packet_id or profile.status == 'gm' \
            or profile.biography_packets.filter(id=bio_packet_id):
        return render(request, '_form.html', context)
    else:
        return redirect('home:dupa')


@login_required
@only_game_masters
def prosoponomikon_first_names_view(request):
    name_groups = NameGroup.objects.prefetch_related(
        'affix_groups__first_names__characters__profile',
        'affix_groups__first_names__auxiliary_group__location',
    )
    context = {
        'page_title': "Imiona",
        'name_groups': name_groups,
    }
    return render(request, 'prosoponomikon/first_names.html', context)


@login_required
@only_game_masters
def prosoponomikon_family_names_view(request):
    family_names = FamilyName.objects.select_related('group')
    family_names = family_names.prefetch_related(
        'characters__profile', 'locations')

    context = {
        'page_title': "Nazwiska",
        'family_names': family_names,
    }
    return render(request, 'prosoponomikon/family_names.html', context)


@login_required
@only_game_masters
def prosoponomikon_character_create_form_view(request):
    """Handle CharacterCreateForm intended for GM."""
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

        messages.success(request, f"Utworzono postać {character}!")
        return redirect('prosoponomikon:character-create')
        
    context = {
        'page_title': "Nowa postać",
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
        zapoznano ze sobą wszystkie postacie [{len(inhabitants)}]!
    """
    messages.success(request, msg)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
