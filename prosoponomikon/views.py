from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Prefetch, Case, When, Value, IntegerField, Q
from django.shortcuts import render, redirect

from imaginarion.models import Picture, PictureImage
from knowledge.forms import BioPacketForm, PlayerBioPacketForm
from knowledge.models import BiographyPacket
from prosoponomikon.forms import CharacterManyGroupsEditFormSet, \
    CharacterGroupsEditFormSetHelper, CharacterSingleGroupEditFormSet
from prosoponomikon.models import Character, CharacterGroup, NameForm, NameContinuum, NameGroup
from rpg_project.utils import handle_inform_form
from users.models import Profile
from toponomikon.models import Location

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
        all_characters = Character.objects.prefetch_related(
            'known_directly', 'known_indirectly')
        players = all_characters.filter(profile__in=Profile.players.all())
        npcs = all_characters.filter(profile__in=Profile.npcs.all())
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
            'known_directly', 'known_indirectly')
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
            'characters__profile__user',
            'characters__known_directly',
            'characters__known_indirectly',
            'characters__name')
        ungrouped = Character.objects.exclude(
            character_groups__in=character_groups)
        ungrouped = ungrouped.prefetch_related(
            'profile__user', 'known_directly', 'known_indirectly')
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
            Prefetch('characters__profile__user', queryset=all_known),
            'characters__known_directly',
            'characters__known_indirectly',
        )
        ungrouped = all_known.exclude(character_groups__in=character_groups)
        ungrouped = ungrouped.prefetch_related(
            'profile__user', 'known_directly', 'known_indirectly')
        
    context = {
        'page_title': 'Prosoponomikon',
        'character_groups': character_groups,
        'ungrouped': ungrouped.select_related('profile'),
    }
    if character_groups:
        return render(request, 'prosoponomikon/characters_grouped.html', context)
    else:
        return redirect('prosoponomikon:ungrouped')


@login_required
def prosoponomikon_character_view(request, character_id):
    profile = request.user.profile
    
    characters = Character.objects.select_related('name')
    if profile.status == 'gm':
        characters = characters.prefetch_related(
            'biography_packets', 'dialogue_packets')
    else:
        known_bio_packets = (profile.biography_packets.all()
                             | profile.authored_bio_packets.all())
        characters = characters.prefetch_related(
            Prefetch('biography_packets', queryset=known_bio_packets))

    character = characters.filter(id=character_id).first()

    # INFORM FORM
    if request.method == 'POST':
        handle_inform_form(request)
    
    context = {
        'page_title': character,
        'character': character,
    }
    if (profile in character.all_known() or profile.character == character
            or profile.status == 'gm'):
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
                
                # for form in formset:
                #     print('one')
                #     if form.is_valid():
                #         print(form.cleaned_data)
                #         # Ignore empty extra-form
                #         if form.cleaned_data == {}:
                #             print(1)
                #             pass
                #         # Existing groups modification/deletion
                #         elif form.cleaned_data.get('id') is not None:
                #             print(2)
                #             if form.cleaned_data.get('DELETE'):
                #                 print(3)
                #                 obj = form.cleaned_data.get('id')
                #                 obj.delete()
                #                 messages.success(
                #                     request, f"Usunięto grupę '{obj.name}'!")
                #                 return redirect('prosoponomikon:grouped')
                #             else:
                #                 print(4)
                #                 obj = form.save()
                #                 print(obj)
                #                 obj.save()
                #                 if form.has_changed():
                #                     print(5)
                #                     messages.success(
                #                         request, f"Zmodyfikowano grupę '{obj.name}'!")
                #                     return redirect('prosoponomikon:grouped')
                #         # New group
                #         else:
                #             print(6)
                #             obj = form.save()
                #             obj.author = profile
                #             obj.save()
                #             obj.characters.set(form.cleaned_data['characters'])
                #             messages.success(
                #                 request, "Utworzono nową grupę '{obj.name}'!")
                #             return redirect('prosoponomikon:grouped')
                #
                #         return redirect('prosoponomikon:grouped')
                #
                #     else: # form invalid
                #         print(7)

            except IntegrityError:
                print(8)
                messages.warning(request, "Nazwy grup muszą być unikalne!")
                return redirect('prosoponomikon:groups-edit')
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

    # # Move 'extra' form to top
    # formset.forms = [formset.forms[-1]] + formset.forms[:-1]
    
    context = {
        'page_title': "Dodaj/Edytuj grupy postaci",
        'formset': formset,
        'formset_helper': CharacterGroupsEditFormSetHelper(status=profile.status),
    }
    return render(request, '_formset.html', context)


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
        
        messages.success(request, f"Zapisano pakiet biograficzny!")
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
def prosoponomikon_names_view(request):
    profile = request.user.profile
    
    # Get all locations that are used as name-areas
    name_areas = Location.objects.filter(names__isnull=False)
    name_areas = name_areas.select_related('location_type')
    name_areas = name_areas.prefetch_related('names__characters')
    name_areas = name_areas.distinct()
    
    context = {
        'page_title': "Imiona",
        'name_areas': name_areas,
    }
    if profile.status == 'gm':
        return render(request, 'prosoponomikon/names.html', context)
    else:
        return redirect('home:dupa')
