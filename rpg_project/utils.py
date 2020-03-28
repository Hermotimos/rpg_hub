import functools
import time

from django.core.mail import send_mail
from django.db import connection, reset_queries

from rpg_project.settings import EMAIL_HOST_USER
from users.models import Profile


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
        subject = f"[RPG] {profile} opowiedział Ci o nowym miejscu!"
        message = f"{profile} opowiedział Ci o miejscu zwanym:" \
                  f" '{location.name}'.\n" \
                  f"Informacje zostały zapisane w Twoim Toponomikonie: \n" \
                  f"{request.build_absolute_uri()}"
        
    elif 'kn_packet' in kwargs:
        kn_packet = kwargs['kn_packet']
        subject = f"[RPG] {profile} przekazał Ci nową wiedzę!"
        message = f"{profile} przekazał Ci wiedzę nt. '{kn_packet.title}'.\n" \
                  f"Więdzę tę możesz odnaleźć w Almanachu pod:" \
                  f" {', '.join(s.name for s in kn_packet.skills.all())}:" \
                  f"{request.get_host()}/knowledge/almanac/"
        
    else:
        subject = 'Błąd'
        message = 'Błąd'

    send_mail(subject, message, sender, receivers)
    return None


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

        print(f"Function : {func.__name__}")
        print(f"Number of Queries : {end_queries - start_queries}")
        print(f"Finished in : {(end - start):.2f}s")
        return result

    return inner_func




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
