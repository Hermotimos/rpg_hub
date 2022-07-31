from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie

from imaginarion.models import Picture, PictureImage, PictureSet
from knowledge.forms import BioPacketForm, PlayerBioPacketForm
from knowledge.models import BiographyPacket
from prosoponomikon.forms import CharacterCreateForm
from prosoponomikon.models import Character, FirstNameGroup, FamilyName, \
    Acquaintanceship, Acquisition
from rpg_project.utils import handle_inform_form, backup_db, auth_profile
from toponomikon.models import Location
from users.models import Profile, User


@cache_page(60 * 5)
@vary_on_cookie
@login_required
@auth_profile(['all'])
def prosoponomikon_acquaintanceships_view(request):
    current_profile = request.current_profile
    acquaintanceships = current_profile.character.acquaintanceships()
    context = {
        'page_title': 'Prosoponomikon',
        'acquaintanceships': acquaintanceships,
    }
    return render(request, 'prosoponomikon/acquaintances.html', context)


@cache_page(60 * 5)
@vary_on_cookie
@login_required
@auth_profile(['all'])
def prosoponomikon_character_view(request, character_id):
    current_profile = request.current_profile
    
    # Declare empty variables
    [
        knowledge_packets, acquaintanceships, acquisitions,
        skill_types_regular, skill_types_priests, skill_types_sorcerers,
        skill_types_theurgists,
        acquisitions_regular, acquisitions_priests, acquisitions_sorcerers,
        acquisitions_theurgists,
        synergies_regular,
    ] = [list() for _ in range(12)]

    if current_profile.character.id == character_id:
        # Players on NPCs viewing their own Characters
        character = current_profile.character
        this_acquaintanceship = None
    else:
        # GM viewing another Character
        if current_profile.can_view_all:
            bio_packets = BiographyPacket.objects.all()
        # Player or NPC viewing another Character
        else:
            # TODO temp
            if request.current_profile.character.fullname in 'Ilen z Astinary, Alora z Astinary, Murkon Lebioda, Syngir':
                return redirect('users:dupa')
            # TODO end temp
            
            bio_packets = (
                current_profile.biography_packets.all()
                | current_profile.authored_bio_packets.all()
            ).prefetch_related('picture_sets')
            
        character = Character.objects.select_related(
            'first_name'
        ).prefetch_related(
            Prefetch('biography_packets', queryset=bio_packets),
            'dialogue_packets'
        ).get(id=character_id)
        
        try:
            this_acquaintanceship = Acquaintanceship.objects.get(
                knowing_character=current_profile.character,
                known_character=character)
        except Acquaintanceship.DoesNotExist:
            # when GM moves between NPCs with open Prosoponomikon
            messages.info(request, "Aktualna Postać nie zna wybranej Postaci!")
            return redirect('prosoponomikon:acquaintanceships')
    
    dialogue_packets = character.dialogue_packets.all()
    biography_packets = character.biography_packets.all()

    # Any Profile viewing own Character or GM viewing any Character
    if current_profile.character.id == character_id or current_profile.status == 'gm':
        
        acquisitions = character.acquisitions_for_character_sheet()
        acquisitions_regular = acquisitions.filter(skill_level__skill__types__kinds__name__in=["Powszechne", "Mentalne"])
        acquisitions_priests = acquisitions.filter(skill_level__skill__types__kinds__name="Moce Kapłańskie")
        acquisitions_sorcerers = acquisitions.filter(skill_level__skill__types__kinds__name="Zaklęcia")
        acquisitions_theurgists = acquisitions.filter(skill_level__skill__types__kinds__name="Moce Teurgiczne")
        
        skill_types = character.skill_types_for_character_sheet()
        skill_types_regular = skill_types.filter(kinds__name__in=["Powszechne", "Mentalne"])
        skill_types_priests = skill_types.filter(kinds__name="Moce Kapłańskie")
        skill_types_sorcerers = skill_types.filter(kinds__name="Zaklęcia")
        skill_types_theurgists = skill_types.filter(kinds__name="Moce Teurgiczne")

        synergies = character.profile.synergies_acquired_with_synergies_levels()
        synergies_regular = synergies.exclude(
            skills__types__kinds__name__in=["Moce Kapłańskie",  "Zaklęcia", "Moce Teurgiczne"])

        knowledge_packets = character.profile.knowledge_packets.prefetch_related(
            'picture_sets__pictures').order_by('title')
        
        acquaintanceships = character.acquaintanceships()
    
    # INFORM FORM
    if request.method == 'POST':
        handle_inform_form(request)

    context = {
        'page_title': character,
        'character': character,
        'acquisitions': acquisitions,
        'acquisitions_regular': acquisitions_regular,
        'acquisitions_priests': acquisitions_priests,
        'acquisitions_sorcerers': acquisitions_sorcerers,
        'acquisitions_theurgists': acquisitions_theurgists,
        'skill_types_regular': skill_types_regular,
        'skill_types_priests': skill_types_priests,
        'skill_types_sorcerers': skill_types_sorcerers,
        'skill_types_theurgists': skill_types_theurgists,
        'synergies_regular': synergies_regular,
        'knowledge_packets': knowledge_packets,
        'biography_packets': biography_packets,
        'dialogue_packets': dialogue_packets,
        'acquaintanceships': acquaintanceships,
        'this_acquaintanceship': this_acquaintanceship,
    }
    if (
            current_profile.character.acquaintanceships().filter(
                known_character=character).exists()
            or current_profile.character == character
            or current_profile.can_view_all
    ):
        return render(request, 'prosoponomikon/character.html', context)
    else:
        return redirect('users:dupa')


@cache_page(60 * 60)
@vary_on_cookie
@login_required
@auth_profile(['all'])
def prosoponomikon_bio_packet_form_view(request, bio_packet_id=0, character_id=0):
    current_profile = request.current_profile

    bio_packet = BiographyPacket.objects.filter(id=bio_packet_id).first()
    character = Character.objects.filter(id=character_id).first()

    if current_profile.status == 'gm':
        form = BioPacketForm(
            data=request.POST or None,
            files=request.FILES or None,
            instance=bio_packet)
    else:
        form = PlayerBioPacketForm(
            data=request.POST or None,
            files=request.FILES or None,
            instance=bio_packet)
    
    if form.is_valid():
        if current_profile.status == 'gm':
            bio_packet = form.save()
        else:
            bio_packet = form.save(commit=False)
            bio_packet.author = current_profile
            bio_packet.save()
            bio_packet.acquired_by.add(current_profile)
            
            pictures = [
                v for k, v in form.cleaned_data.items()
                if 'picture' in k and v is not None
            ]

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
                    [Autor: {current_profile.character.first_name} - {now}]
                """
                new_picture_set = PictureSet.objects.create(title=title)
                new_picture_set.pictures.set(new_pictures)
                bio_packet.picture_sets.add(new_picture_set)

        character.biography_packets.add(bio_packet)
        
        messages.success(request, "Zapisano Biogram!")
        return redirect('prosoponomikon:character', character_id)

    else:
        messages.warning(request, form.errors)

    context = {
        'page_title': f"{character}: {bio_packet.title}" if bio_packet else f"Biogram: {character}",
        'form': form,
    }
    if not bio_packet_id or current_profile.status == 'gm' \
            or current_profile.biography_packets.filter(id=bio_packet_id):
        return render(request, '_form.html', context)
    else:
        return redirect('users:dupa')


@login_required
@auth_profile(['gm'])
def prosoponomikon_first_names_view(request):
    name_groups = FirstNameGroup.objects.prefetch_related(
        'affix_groups__first_names__characters__profile',
        'affix_groups__first_names__auxiliary_group__location',
    )
    context = {
        'page_title': "Imiona",
        'name_groups': name_groups,
    }
    return render(request, 'prosoponomikon/first_names.html', context)


@login_required
@auth_profile(['gm'])
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
@auth_profile(['gm'])
def prosoponomikon_character_create_form_view(request):
    """Handle CharacterCreateForm intended for GM."""
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
        'page_title': "Nowa Postać",
        'form': form,
    }
    return render(request, '_form.html', context)


@login_required
@auth_profile(['gm'])
def prosoponomikon_acquaintances_view(request, location_id):
    """Make everybody know directly everybody in a given Location."""

    # TODO update this view
    
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
