from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from history.models import Thread, SpecificLocation, GeneralLocation
from rules.models import Skill, Synergy, CharacterClass, CharacterProfession, EliteClass, EliteProfession, WeaponClass, WeaponType
from rpg_project.utils import query_debugger


@query_debugger
@login_required
def reload_main_view(request):
    context = {
        'page_title': 'Przeładowanie sorting_name'
    }
    if request.user.profile.character_status == 'gm':
        return render(request, 'reload/reload_main.html', context)
    else:
        return redirect('home:dupa')


@query_debugger
@login_required
def reload_history(request):
    if request.user.profile.character_status == 'gm':

        for obj in Thread.objects.all():
            obj.save()
        for obj in GeneralLocation.objects.all():
            obj.save()
        for obj in SpecificLocation.objects.all():
            obj.save()

        messages.info(request, f'Przeładowano "sorting_name" dla aplikacji "history"!')
        return redirect('reload:reload-main')
    else:
        return redirect('home:dupa')


@query_debugger
@login_required
def reload_rules(request):
    if request.user.profile.character_status == 'gm':

        for obj in Skill.objects.all():
            obj.save()
        for obj in Synergy.objects.all():
            obj.save()
        for obj in CharacterClass.objects.all():
            obj.save()
        for obj in CharacterProfession.objects.all():
            obj.save()
        for obj in EliteClass.objects.all():
            obj.save()
        for obj in EliteProfession.objects.all():
            obj.save()
        for obj in WeaponClass.objects.all():
            obj.save()
        for obj in WeaponType.objects.all():
            obj.save()

        messages.info(request, f'Przeładowano "sorting_name" dla aplikacji "rules"!')
        return redirect('reload:reload-main')
    else:
        return redirect('home:dupa')


