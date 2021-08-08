from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.shortcuts import render, redirect

from chronicles.models import GameEvent
from imaginarion.models import PictureImage
from prosoponomikon.models import Character
from prosoponomikon.models import NonGMCharacter
from rules.models import (
    Skill, SkillLevel,
    Synergy, SynergyLevel,
    Profession,
    Klass,
    EliteProfession,
    EliteKlass,
    WeaponType,
    Weapon,
)
from toponomikon.models import Location
from users.models import Profile


@login_required
def reload_main_view(request):
    context = {
        'page_title': 'Przeładowanie sorting_name'
    }
    if request.user.profile.status == 'gm':
        return render(request, 'reload/reload_main.html', context)
    else:
        return redirect('home:dupa')


@login_required
def reload_chronicles(request):
    if request.user.profile.status == 'gm':
        for obj in GameEvent.objects.all():
            obj.save()
        messages.info(request, f'Przeładowano "GameEvent"!')
        return redirect('reload:reload-main')
    else:
        return redirect('home:dupa')


@login_required
def reload_imaginarion(request):
    if request.user.profile.status == 'gm':
        for obj in PictureImage.objects.all():
            print(obj.used_in_pics.first().description)
            obj.description = obj.used_in_pics.first().description
            obj.save()
        messages.info(request, f'Przeładowano "PictureImage" dla "imaginarion"!')
        return redirect('reload:reload-main')
    else:
        return redirect('home:dupa')


@login_required
def reload_prosoponomikon(request):
    if request.user.profile.status == 'gm':
        for obj in Character.objects.all():
            
            # TODO REMOVE WHEN DONE
            # if "z" in obj.name:
            #     indx = obj.name.index("z")
            #     obj.cognomen = obj.name[indx:]
            
            # if obj.name:
            #     FirstName.objects.create(form=obj.name)
            
            obj.save()
        messages.info(request,
                      f'Przeładowano "Character" dla "prosoponomikon"!')
        return redirect('reload:reload-main')
    else:
        return redirect('home:dupa')


@login_required
def reload_rules(request):
    if request.user.profile.status == 'gm':

        for obj in Skill.objects.all():
            obj.save()
        for obj in SkillLevel.objects.all():
            obj.save()

        for obj in Synergy.objects.all():
            obj.save()
        for obj in SynergyLevel.objects.all():
            obj.save()

        for obj in Profession.objects.all():
            obj.save()
        for obj in Klass.objects.all():
            obj.save()

        for obj in EliteProfession.objects.all():
            obj.save()
        for obj in EliteKlass.objects.all():
            obj.save()

        for obj in WeaponType.objects.all():
            obj.save()
        for obj in Weapon.objects.all():
            obj.save()

        messages.info(request, f'Przeładowano "sorting_name" dla aplikacji "rules"!')
        return redirect('reload:reload-main')
    else:
        return redirect('home:dupa')
    

@login_required
def reload_toponomikon(request):
    if request.user.profile.status == 'gm':
        for obj in Location.objects.all():
            obj.save()
        messages.info(request, f'Przeładowano "Location" dla "toponomikon"!')
        return redirect('reload:reload-main')
    else:
        return redirect('home:dupa')
    
    
@login_required
def refresh_content_types(request):
    """Remove stale content types."""
    if request.user.profile.status == 'gm':
        deleted = []
        for c in ContentType.objects.all():
            if not c.model_class():
                deleted.append(c.__dict__)
                c.delete()
        messages.info(request, f"Usunięto content types: {deleted or 0}")
        return redirect('reload:reload-main')
    else:
        return redirect('home:dupa')


#  ---------------------------------------------------------------------


@login_required
def todos_view(request):
    profile = request.user.profile
    characters = NonGMCharacter.objects.all()
    
    characters_no_frequented_location = characters.filter(frequented_locations=None)
    characters_no_description = characters.filter(description__exact="")
    
    profiles_no_image = Profile.objects.filter(
        Q(image__icontains="square") | Q(image__exact=""))
    
    locations_no_image = Location.objects.filter(main_image=None)
    locations_no_description = Location.objects.filter(description__exact="")
    
    game_event_no_known = GameEvent.objects.filter(
        known_directly=None).filter(known_indirectly=None)
   
    context = {
        'page_title': 'TODOs',
        'characters_no_frequented_location': characters_no_frequented_location,
        'characters_no_description': characters_no_description,
        'profiles_no_image': profiles_no_image,
        'locations_no_image': locations_no_image,
        'locations_no_description': locations_no_description,
        'game_event_no_known': game_event_no_known,
    }
    
    if profile.status == 'gm':
        return render(request, 'reload/todos.html', context)
    else:
        return redirect('home:dupa')


