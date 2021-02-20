from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render, redirect

from chronicles.models import Thread, GameEvent
from imaginarion.models import Picture, PictureImage
from prosoponomikon.models import Character
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
        for obj in Thread.objects.all():
            obj.save()
        for obj in GameEvent.objects.all():
            obj.save()
        messages.info(request, f'Przeładowano "Thread" i "GameEvent"!')
        return redirect('reload:reload-main')
    else:
        return redirect('home:dupa')


@login_required
def reload_imaginarion(request):
    if request.user.profile.status == 'gm':
        # for obj in Picture.objects.all():
        #     # obj.image_replacement_field = PictureImage.objects.create(
        #     #     image=obj.image,
        #     #     description=obj.description,
        #     # )
        #     obj.save()
        for obj in PictureImage.objects.all():
            obj.save()
        messages.info(request, f'Przeładowano "PictureImage" dla "imaginarion"!')
        return redirect('reload:reload-main')
    else:
        return redirect('home:dupa')


@login_required
def reload_prosoponomikon(request):
    if request.user.profile.status == 'gm':
        for obj in Character.objects.all():
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
    
    


