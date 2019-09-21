from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages


@login_required
def home_view(request):
    return render(request, 'home/home.html')


@login_required
def dupa_view(request):
    return render(request, 'home/dupa.html', {'page_title': 'Dupa!'})


@login_required
def reload_sorting_names_view(request):
    if request.user.profile.character_status == 'gm':
        from rules.models import CharacterClass, EliteClass, CharacterProfession, EliteProfession, Skill, Synergy
        from history.models import Thread, GeneralLocation, SpecificLocation

        # rules app
        for o in Skill.objects.all():
            o.save()
        for o in Synergy.objects.all():
            o.save()
        for o in CharacterClass.objects.all():
            o.save()
        for o in EliteClass.objects.all():
            o.save()
        for o in CharacterProfession.objects.all():
            o.save()
        for o in EliteProfession.objects.all():
            o.save()

        # history app
        for o in Thread.objects.all():
            o.save()
        for o in GeneralLocation.objects.all():
            o.save()
        for o in SpecificLocation.objects.all():
            o.save()

        messages.info(request, f'Przeładowano "sorting names"!')
        return redirect('home:home')
    else:
        return redirect('home:dupa')
