from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.db.models.functions import Substr, Lower
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect

from imaginarion.models import Picture, PictureImage, PictureSet
from knowledge.forms import BioPacketForm, PlayerBioPacketForm
from knowledge.models import BiographyPacket
from prosoponomikon.forms import CharacterCreateForm
from prosoponomikon.models import Character, NameGroup, FamilyName
from rpg_project.settings import get_secret
from rpg_project.utils import handle_inform_form, backup_db, only_game_masters
from toponomikon.models import Location
from users.models import Profile, User


@login_required
def prosoponomikon_characters_view(request):
    profile = Profile.objects.get(id=request.session['profile_id'])
    
    all_characters = profile.characters_known_annotated()
    all_characters = all_characters.annotate(initial=Lower(Substr('profile__character_name_copy', 1, 1)))
    
    context = {
        'current_profile': profile,
        'page_title': 'Prosoponomikon',
        'all_characters': all_characters,
    }
    return render(request, 'prosoponomikon/characters.html', context)


@login_required
def prosoponomikon_character_view(request, character_id):
    current_profile = Profile.objects.get(id=request.session['profile_id'])
    
    if current_profile.character.id == character_id:
        # Players viewing their own Characters
        character = current_profile.character
    else:
        # Player or GM viewing other Characters
        known_bio_packets = (current_profile.biography_packets.all() | current_profile.authored_bio_packets.all()).prefetch_related('picture_sets')
        characters = Character.objects.select_related('first_name')
        characters = characters.prefetch_related(
            Prefetch('biography_packets', queryset=known_bio_packets),
            'dialogue_packets')
        character = characters.get(id=character_id)

    # Player viewing own Character or GM viewing any Character
    if current_profile.character.id == character_id or current_profile.status == 'gm':
        skills = character.profile.skills_acquired_with_skill_levels()
        synergies = character.profile.synergies_acquired_with_synergies_levels()
        knowledge_packets = character.profile.knowledge_packets.prefetch_related(
            'picture_sets__pictures').order_by('title')
        known_characters = character.profile.characters_known_annotated()
    
    # Player viewing other Characters
    else:
        skills, knowledge_packets, known_characters, synergies = [], [], [], []
        
    # INFORM FORM
    if request.method == 'POST':
        handle_inform_form(request)
    
    context = {
        'current_profile': current_profile,
        'page_title': character,
        'character': character,
        'skills': skills,
        'synergies': synergies,
        'knowledge_packets': knowledge_packets,
        'known_characters': known_characters,
    }
    if (current_profile in character.all_known() or current_profile.character == character
            or current_profile.can_view_all):
        return render(request, 'prosoponomikon/character.html', context)
    else:
        return redirect('users:dupa')


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
        profile = Profile.objects.create(
            user=User.objects.get(username=form.cleaned_data['username']),
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
        [character.participants.add(i.profile) for i in inhabitants]

    msg = f"""
        {location.name}:
        zapoznano ze sobą wszystkie Postacie [{len(inhabitants)}]!
    """
    messages.success(request, msg)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
