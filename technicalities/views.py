from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.files import File
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.utils.safestring import mark_safe

from chronicles.models import GameEvent
from imaginarion.models import PictureImage
from prosoponomikon.models import Character, NonGMCharacter
from rpg_project.utils import backup_db, only_game_masters
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
from news.models import News, NewsAnswer


@login_required
@only_game_masters
def todos_view(request):
    profile = Profile.objects.get(id=request.session['profile_id'])
    
    characters = NonGMCharacter.objects.all()
    
    characters_no_frequented_location = characters.filter(
        frequented_locations=None)
    characters_no_description = characters.filter(description__exact="")
    
    profiles_no_image = Profile.objects.filter(
        Q(image__icontains="square") | Q(image__exact=""))
    
    locations_no_image = Location.objects.filter(main_image=None)
    locations_no_description = Location.objects.filter(description__exact="")
    
    game_event_no_known = GameEvent.objects.filter(
        known_directly=None).filter(known_indirectly=None)
    
    skills_no_skill_type = Skill.objects.filter(types=None)
    skills_no_allowed_profile = Skill.objects.filter(allowed_profiles=None)
    
    context = {
        'current_profile': profile,
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
@only_game_masters
def backup_db_view(request):
    backup_db(reason="manual")
    messages.info(request, 'Wykonano backup bazy na serwerze!')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
@only_game_masters
def download_db(request):
    db_path = settings.DATABASES['default']['NAME']
    db_file = File(open(db_path, "rb"))
    response = HttpResponse(db_file, content_type='application/x-sqlite3')
    response['Content-Disposition'] = 'attachment; filename=db.sqlite3'
    response['Content-Length'] = db_file.size
    return response


# ============================================================================


@login_required
@only_game_masters
def reload_main_view(request):
    profile = Profile.objects.get(id=request.session['profile_id'])
    context = {
        'current_profile': profile,
        'page_title': 'Przeładowanie sorting_name'
    }
    return render(request, 'technicalities/reload_main.html', context)


@login_required
@only_game_masters
def reload_chronicles(request):
    for obj in GameEvent.objects.all():
        obj.save()
    messages.info(request, 'Przeładowano "GameEvent"!')
    return redirect('technicalities:reload-main')


@login_required
@only_game_masters
def reload_imaginarion(request):
    for obj in PictureImage.objects.all():
        # print(obj.used_in_pics.first().description)
        obj.description = obj.used_in_pics.first().description
        obj.save()
    messages.info(request, f'Przeładowano "PictureImage" dla "imaginarion"!')
    return redirect('technicalities:reload-main')


@login_required
@only_game_masters
def reload_prosoponomikon(request):
    for obj in Character.objects.all():
        obj.save()
    messages.info(request, 'Przeładowano "Characters" w "prosoponomikon"!')
    return redirect('technicalities:reload-main')


@login_required
@only_game_masters
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

    messages.info(request, 'Przeładowano "sorting_name" dla "rules"!')
    return redirect('technicalities:reload-main')


@login_required
@only_game_masters
def reload_toponomikon(request):
    for obj in Location.objects.all():
        obj.save()
    messages.info(request, 'Przeładowano "Location" dla "toponomikon"!')
    return redirect('technicalities:reload-main')


@login_required
@only_game_masters
def reload_news(request):
    from news.models import Topic as NewsTopic, News, NewsAnswer
    from communications.models import Option, Announcement, Topic, Statement
    from django.db import transaction

    with transaction.atomic():
        for news_topic in NewsTopic.objects.all():
            topic = Topic.objects.create(
                title=news_topic.title, order_no=news_topic.order_no,
                created_at=news_topic.created_at)
            
            for news in news_topic.news.all():
                announcement = Announcement.objects.create(
                    topic=topic, title=news.title, kind='Announcement',
                    created_at=news.created_at)
                announcement.save()
                announcement.known_directly.set(news.allowed_profiles.all())
                announcement.known_directly.add(Profile.objects.get(status='gm'))
                announcement.followers.set(news.followers.all())
                print(announcement.title)
                
                for answer in news.news_answers.all():
                    statement = Statement.objects.create(
                        text=answer.text, thread=announcement, author=answer.author,
                        created_at=answer.created_at, image=answer.image,
                    )
                    statement.save()
                    # print(statement.text[:20], statement.id)
                    statement.seen_by.set(answer.seen_by.all())
            
    messages.info(request, 'Przeładowano NEWS->COMMUNICATIONS!')
    return redirect('technicalities:reload-main')


@login_required
@only_game_masters
def reload_debates(request):
    # from debates.models import Debate as OldDebate, Remark, Topic as OldTopic
    from communications.models import Option, Debate, Topic, Statement
    from django.db import transaction

    with transaction.atomic():
        for old_topic in OldTopic.objects.all():
            new_topic = Topic.objects.create(
                title=old_topic.title, order_no=old_topic.order_no,
                created_at=old_topic.created_at)
            new_topic.created_at = old_topic.created_at
            new_topic.save(update_fields=['created_at'])

            for debate in old_topic.debates.all():
                new_debate = Debate.objects.create(
                    topic=new_topic, title=debate.title, kind='Debate',
                    is_ended=debate.is_ended, is_exclusive=debate.is_exclusive,
                    created_at=debate.created_at)
                new_debate.save()
                new_debate.created_at = debate.created_at
                new_debate.save(update_fields=['created_at'])

                new_debate.known_directly.set(debate.known_directly.all())
                new_debate.known_directly.add(Profile.objects.get(status='gm'))
                new_debate.followers.set(debate.known_directly.all())
                new_debate.followers.add(Profile.objects.get(status='gm'))
                
                # TODO attach events to new debates
                events = debate.events.all()
                new_debate.eventss.set(events)
                # new_debate.save()
                print(new_debate.title)
                
                for remark in debate.remarks.all():
                    statement = Statement.objects.create(
                        text=remark.text, thread=new_debate, author=remark.author,
                        created_at=remark.created_at,
                    )
                    statement.save()
                    statement.image = remark.image
                    statement.save()
                    statement.created_at = remark.created_at
                    statement.save(update_fields=['created_at'])
                    statement.seen_by.set(remark.seen_by.all())
                    
                    if remark.image:
                        print('    ', remark.image)
                        print('    ', remark.text[:50])
                        print()


    messages.info(request, 'Przeładowano DEBATES->COMMUNICATIONS!')
    return redirect('technicalities:reload-main')


@login_required
@only_game_masters
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


#  ---------------------------------------------------------------------


