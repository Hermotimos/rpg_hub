from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from chronicles.models import Thread, GameEvent
from toponomikon.models import Location
from rules.models import Skill, SkillLevel, Synergy, SynergyLevel, Profession, Klass, EliteProfession, \
    EliteKlass, WeaponType, Weapon
from prosoponomikon.models import Persona


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
def reload_history(request):
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
def reload_toponomikon(request):
    if request.user.profile.status == 'gm':
        for obj in Location.objects.all():
            obj.save()
        messages.info(request, f'Przeładowano "sorting_name" dla aplikacji "toponomikon"!')
        return redirect('reload:reload-main')
    else:
        return redirect('home:dupa')\
        
        
@login_required
def reload_prosoponomikon(request):
    if request.user.profile.status == 'gm':
        for obj in Persona.objects.all():
            obj.save()
        messages.info(request, f'Przeładowano "sorting_name" dla aplikacji "prosoponomikon"!')
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


