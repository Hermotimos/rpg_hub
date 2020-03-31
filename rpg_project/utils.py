import functools
import time

from django.core.mail import send_mail
from django.db import connection, reset_queries

from rpg_project.settings import EMAIL_HOST_USER
from users.models import Profile


def create_sorting_name(obj):
    name = str(obj).lower()
    name = name.replace('a', 'aa')
    name = name.replace('ą', 'aą')
    name = name.replace('c', 'cc')
    name = name.replace('ć', 'cć')
    name = name.replace('e', 'ee')
    name = name.replace('ę', 'eę')
    name = name.replace('l', 'll')
    name = name.replace('ł', 'lł')
    name = name.replace('n', 'nn')
    name = name.replace('ń', 'nń')
    name = name.replace('o', 'oo')
    name = name.replace('ó', 'oó')
    name = name.replace('s', 'ss')
    name = name.replace('ś', 'sś')
    name = name.replace('z', 'zz')
    name = name.replace('ż', 'zż')
    name = name.replace('ź', 'zź')
    return name


def query_debugger(func):
    """
    Source of query_debugger: https://medium.com/@goutomroy/django-select-related-and-prefetch-related-f23043fd635d
    """
    @functools.wraps(func)
    def inner_func(*args, **kwargs):

        reset_queries()
        start_queries = len(connection.queries)

        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        
        end_queries = len(connection.queries)

        print(f'Function : {func.__name__}')
        print(f'Number of Queries : {end_queries - start_queries}')
        print(f'Finished in : {(end - start):.2f}s')
        return result

    return inner_func


def send_emails(request, profile_ids, **kwargs):
    profile = request.user.profile
    sender = EMAIL_HOST_USER
    receivers = [
        p.user.email for p in Profile.objects.filter(id__in=profile_ids)
    ]
    if profile.status != 'gm':
        receivers.append('lukas.kozicki@gmail.com')
    
    if 'location' in kwargs:
        location = kwargs['location']
        subject = '[RPG] Transfer wiedzy!'
        message = f"{profile} opowiedział/a Ci o miejscu zwanym" \
                  f" '{location.name}'." \
                  f"\nInformacje zostały zapisane w Twoim Toponomikonie: " \
                  f"\n{request.build_absolute_uri()}"
    
    elif 'kn_packet' in kwargs:
        kn_packet = kwargs['kn_packet']
        subject = '[RPG] Transfer wiedzy!'
        message = f"{profile} przekazał/a Ci wiedzę nt. '{kn_packet.title}'." \
                  f"\nWiędzę tę możesz odnaleźć w Almanachu pod:" \
                  f" {', '.join(s.name for s in kn_packet.skills.all())}:" \
                  f"\n{request.get_host()}/knowledge/almanac/"
    
    elif 'debate_new_topic' in kwargs:
        debate = kwargs['debate_new_topic']
        subject = '[RPG] Nowa narada w nowym temacie!'
        message = f"{profile} włączył/a Cię do nowej narady '{debate.name}' " \
                  f"w nowym temacie '{debate.topic}'." \
                  f"\nWeź udział w naradzie:\n" \
                  f"{request.get_host()}/debates/topic:{debate.topic.id}/debate:{debate.id}/"
    
    elif 'debate_new' in kwargs:
        debate = kwargs['debate_new']
        subject = '[RPG] Nowa narada!'
        message = f"{profile} włączył/a Cię do nowej narady '{debate.name}' " \
                  f"w temacie '{debate.topic}'." \
                  f"\nWeź udział w naradzie:\n" \
                  f"{request.get_host()}/debates/topic:{debate.topic.id}/debate:{debate.id}/"
    
    elif 'debate_info' in kwargs:
        debate = kwargs['debate_info']
        subject = '[RPG] Dołączenie do narady!'
        message = f"{profile} dołączył/a Cię do narady '{debate.name}' " \
                  f"w temacie '{debate.topic}'." \
                  f"\nWeź udział w naradzie:\n{request.build_absolute_uri()}"
    
    elif 'debate_remark' in kwargs:
        debate = kwargs['debate_remark']
        subject = '[RPG] Wypowiedź w naradzie!'
        message = f"{profile} zabrał/a głos w naradzie '{debate.name}' " \
                  f"w temacie '{debate.topic}'." \
                  f"\nWeź udział w naradzie:\n{request.build_absolute_uri()}"
    
    elif 'timeline_event' in kwargs:
        event = kwargs['timeline_event']
        subject = "[RPG] Nowa opowieść o wydarzeniach!"
        message = f"{profile} rozprawia o swoich przygodach.\n" \
                  f"'{event.date()} rozegrało się co następuje...\n " \
                  f"Wydarzenie zostało zapisane w Twoim Kalendarium."

    elif 'chronicle_event' in kwargs:
        event = kwargs['chronicle_event']
        subject = "[RPG] Nowa opowieść o wydarzeniach!"
        message = f"{profile} rozprawia o swoich przygodach.\n" \
                  f"Podczas przygody '{event.game.title}' " \
                  f"rozegrało się co następuje:...\n" \
                  f"Wydarzenie zostało zapisane w Twojej Kronice: " \
                  f"{request.get_host()}/history/chronicle/one-game:{event.game.id}:0/"

    else:
        subject = 'Błąd'
        message = f"URL: {request.build_absolute_uri()}\n" \
                  f"kwargs: {kwargs}"
    print(kwargs)
    send_mail(subject, message, sender, receivers)
    return None
