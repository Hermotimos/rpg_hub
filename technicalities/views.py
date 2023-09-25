import os
from django.core.cache import cache
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.utils.safestring import mark_safe

from chronicles.models import GameEvent
from imaginarion.models import PictureImage
from prosoponomikon.models import Character, NonGMCharacter
from rpg_project.utils import backup_db, update_db, auth_profile
from rules.models import (
    Skill, SkillLevel,
    Synergy, SynergyLevel,
    Profession,
    WeaponType,
    Plate,
    Shield,
)
from toponomikon.models import Location
from users.models import Profile


@login_required
@auth_profile(['gm'])
def todos_view(request):
    characters = NonGMCharacter.objects.all()

    characters_no_frequented_location = characters.filter(
        frequented_locations=None)
    characters_no_description = characters.filter(description__exact="")

    profiles_no_image = Profile.objects.filter(
        Q(image__icontains="square") | Q(image__exact=""))

    locations_no_image = Location.objects.filter(main_image=None)
    locations_no_description = Location.objects.filter(description__exact="")

    game_event_no_known = GameEvent.objects.filter(
        participants=None).filter(informees=None)

    skills_no_skill_type = Skill.objects.filter(types=None)
    skills_no_allowed_profile = Skill.objects.filter(allowees=None)

    context = {
        'page_title': 'TODOs',
        'characters_no_frequented_location': characters_no_frequented_location,
        'characters_no_description': characters_no_description,
        'profiles_no_image': profiles_no_image,
        'locations_no_image': locations_no_image,
        'locations_no_description': locations_no_description,
        'game_event_no_known': game_event_no_known,
        'skills_no_skill_type': skills_no_skill_type,
        'skills_no_allowed_profile': skills_no_allowed_profile,
    }
    return render(request, 'technicalities/todos.html', context)


@login_required
@auth_profile(['gm'])
def backup_db_view(request):
    if not os.environ.get('COMPUTERNAME'):
        messages.warning(request, 'Funkcja dostępna tylko w developmencie!')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    backup_db()

    messages.info(request, 'Wykonano lokalny backup bazy produkcyjnej!')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
@auth_profile(['gm'])
def update_local_db_view(request):
    if not os.environ.get('COMPUTERNAME'):
        messages.warning(request, 'Funkcja dostępna tylko w developmencie!')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    update_db(
        reason="dev",
        src=settings.GCP_DATABASE_DNS,
        dst=settings.DEV_DATABASE_DNS)

    messages.info(request, 'Wykonano lokalny backup bazy dev!')
    messages.info(request, 'Nadpisano lokalną bazę danymi z bazy GCP!')
    logout(request)
    return redirect('users:login')


@login_required
@auth_profile(['gm'])
def update_production_db_view(request):
    if not os.environ.get('COMPUTERNAME'):
        messages.warning(request, 'Funkcja dostępna tylko w developmencie!')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    update_db(
        reason="prod",
        src=settings.DEV_DATABASE_DNS,
        dst=settings.GCP_DATABASE_DNS)

    messages.info(request, 'Wykonano lokalny backup bazy prod!')
    messages.info(request, 'Nadpisano bazę produkcyjną z bazy lokalnej!')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
@auth_profile(['gm'])
def allow_game_masters_to_all(request):
    models = [
        Skill, Synergy, Profession, WeaponType, Plate, Shield,
    ]
    for Model in models:
        print(f"Processing Model: {Model}")
        for obj in Model.objects.all():
            obj.allowees.add(*Profile.objects.filter(status="gm"))
            obj.save()

    messages.info(
        request,
        f"Udostępniono Mistrzom Gry obiekty z następujących Modeli: {models}")
    return redirect('technicalities:reload-main')


@login_required
@auth_profile(['gm'])
def cleanup_rules_objects(request):
    from rules.models import Factor, Modifier, ConditionalModifier, DamageType

    for factor in Factor.objects.all():
        if not factor.modifiers.exists():
            print('Factor:', factor)
            factor.delete()

    for modifier in Modifier.objects.all():
        if not modifier.conditional_modifiers.exists():
            print('Modifier:', modifier)
            modifier.delete()

    for conditional_modifier in ConditionalModifier.objects.all():
        if not conditional_modifier.perks.exists():
            print('ConditionalModifier:', conditional_modifier)
            conditional_modifier.delete()

    for damage_type in DamageType.objects.all():
        if not damage_type.weapon_types.exists():
            print('DamageType:', damage_type)
            damage_type.delete()

    messages.info(request, f"Usunięto obiekty nieposiadające obiektów powiązanych - zobacz printy w logu.")
    return redirect('technicalities:reload-main')


@login_required
@auth_profile(['gm'])
def refresh_content_types(request):
    """Remove stale content types."""
    deleted = []
    for c in ContentType.objects.all():
        if not c.model_class():
            deleted.append(c.__dict__)
            c.delete()
    deleted = "<br>".join([str(dict_) for dict_ in deleted]) if deleted else 0
    messages.info(request, mark_safe(f"Usunięto content types:\n{deleted}"))
    return redirect('technicalities:reload-main')


@login_required
@auth_profile(['all'])
def clear_cache_all_view(request):
    cache.clear()
    messages.info(
        request,
        "Zawartość strony została odświeżona! Niektóre elementy mogą działać wolniej przy pierwszym ładowaniu.")
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
@auth_profile(['gm'])
def example_json_view(request):
    """
    Example view returning JSON for playing with AJAX.

    function loadDoc() {
        const xhttp = new XMLHttpRequest();
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                console.log(this.responseText)
            }
        };
        xhttp.open("GET", "http://127.0.0.1:8000/technicalities/example-json/");
        xhttp.send();
    }

    loadDoc()

    """
    from django.http import JsonResponse
    return JsonResponse(
        {"first": 1, "second": "temp Syngir, Murkon", "third": [1, 2, 3, 4]}
    )

"""
AJAX


"""

# ============================================================================


@login_required
@auth_profile(['gm'])
def reload_main_view(request):
    context = {
        'page_title': 'Przeładowanie modeli'
    }
    return render(request, 'technicalities/reload_main.html', context)


@login_required
@auth_profile(['gm'])
def reload_chronicles(request):
    for obj in GameEvent.objects.all():
        obj.save()
    messages.info(request, 'Przeładowano "GameEvent"!')
    return redirect('technicalities:reload-main')


@login_required
@auth_profile(['gm'])
def reload_imaginarion(request):
    for obj in PictureImage.objects.all():
        # print(obj.pictures.first().description)
        obj.description = obj.pictures.first().description
        obj.save()
    messages.info(request, f'Przeładowano "PictureImage" dla "imaginarion"!')
    return redirect('technicalities:reload-main')


@login_required
@auth_profile(['gm'])
def reload_prosoponomikon(request):
    for obj in Character.objects.all():
        obj.save()
    messages.info(request, 'Przeładowano "Characters" w "prosoponomikon"!')
    return redirect('technicalities:reload-main')


@login_required
@auth_profile(['gm'])
def reload_rules(request):
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

    for obj in WeaponType.objects.all():
        obj.save()

    messages.info(request, 'Przeładowano modele dla "rules"!')
    return redirect('technicalities:reload-main')


@login_required
@auth_profile(['gm'])
def reload_toponomikon(request):
    for obj in Location.objects.all():
        obj.save()
    messages.info(request, 'Przeładowano "Location" dla "toponomikon"!')
    return redirect('technicalities:reload-main')

