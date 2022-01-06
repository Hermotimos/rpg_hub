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
    
    context = {
        'current_profile': profile,
        'page_title': 'TODOs',
        'characters_no_frequented_location': characters_no_frequented_location,
        'characters_no_description': characters_no_description,
        'profiles_no_image': profiles_no_image,
        'locations_no_image': locations_no_image,
        'locations_no_description': locations_no_description,
        'game_event_no_known': game_event_no_known,
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
def reorder_news(request):
    from news.models import Topic, News, NewsAnswer
    
    topic = Topic.objects.get(id=2)
    print(topic.title)
    existing_news = topic.news.all()
    
    allowed_profiles = set()
    created_at = min([news.created_at for news in existing_news])
    for news in existing_news:
        allowed_profiles.update([p for p in news.allowed_profiles.all()])

    # print(created_at)
    # print(allowed_profiles)
    new_big_news = News.objects.create(
        topic=topic,
        title='Zasady prowadzenia Narad',
        created_at=created_at,
    )
    new_big_news.allowed_profiles.set(allowed_profiles)
    new_big_news.followers.set([p for p in allowed_profiles if p.is_active])
    #
    import datetime
    # NewsAnswer.objects.create(
    #     news=new_big_news,
    #     author=Profile.objects.get(status='gm'),
    #     text='[Konwersacja o charakterze ciągłym - swobodnie piszcie w temacie]',
    #     created_at=(created_at - datetime.timedelta(days=1))
    # )
        
    for news in existing_news.filter(title__icontains='narady'):
        print(news.title)
        for news_answer in news.news_answers.all():
            news_answer.news_id = new_big_news.id
            news_answer.save()

    messages.info(request, 'Zagregowano NEWS!')
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


