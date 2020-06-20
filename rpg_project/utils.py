import os

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.mail import send_mail

from rpg_project.settings import EMAIL_HOST_USER
from users.models import Profile


class ReplaceFileStorage(FileSystemStorage):

    def get_available_name(self, name, max_length=None):
        """
        Returns a filename that's free on the target storage system, and
        available for new content to be written to.
        Found at http://djangosnippets.org/snippets/976/
        This file storage solves overwrite on upload problem.
        """
        # If the filename already exists, remove it
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name
    
    
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
                  f"\n{request.build_absolute_uri()}\n"
    
    elif 'kn_packet' in kwargs:
        kn_packet = kwargs['kn_packet']
        subject = '[RPG] Transfer wiedzy!'
        message = f"{profile} przekazał/a Ci wiedzę nt. '{kn_packet.title}'." \
                  f"\nWiędzę tę możesz odnaleźć w Almanachu pod:" \
                  f" {', '.join(s.name for s in kn_packet.skills.all())}:" \
                  f"\n{request.get_host()}/knowledge/almanac/\n"
    
    elif 'debate_new_topic' in kwargs:
        debate = kwargs['debate_new_topic']
        subject = '[RPG] Nowa narada w nowym temacie!'
        message = f"{profile} włączył/a Cię do nowej narady '{debate.name}' " \
                  f"w nowym temacie '{debate.topic}'." \
                  f"\nWeź udział w naradzie:\n" \
                  f"{request.get_host()}/debates/topic:{debate.topic.id}/debate:{debate.id}/\n"
    
    elif 'debate_new' in kwargs:
        debate = kwargs['debate_new']
        subject = '[RPG] Nowa narada!'
        message = f"{profile} włączył/a Cię do nowej narady '{debate.name}' " \
                  f"w temacie '{debate.topic}'." \
                  f"\nWeź udział w naradzie:\n" \
                  f"{request.get_host()}/debates/topic:{debate.topic.id}/debate:{debate.id}/\n"
    
    elif 'debate_info' in kwargs:
        debate = kwargs['debate_info']
        subject = '[RPG] Dołączenie do narady!'
        message = f"{profile} dołączył/a Cię do narady '{debate.name}' " \
                  f"w temacie '{debate.topic}'." \
                  f"\nWeź udział w naradzie:" \
                  f"\n{request.build_absolute_uri()}\n"
    
    elif 'debate_remark' in kwargs:
        debate = kwargs['debate_remark']
        subject = '[RPG] Wypowiedź w naradzie!'
        message = f"{profile} zabrał/a głos w naradzie '{debate.name}' " \
                  f"w temacie '{debate.topic}'." \
                  f"\nWeź udział w naradzie:" \
                  f"\n{request.build_absolute_uri()}#page-bottom\n"
    
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
                  f"rozegrało się co następuje...\n" \
                  f"Wydarzenie zostało zapisane w Twojej Kronice: " \
                  f"{request.get_host()}/history/chronicle/one-game:{event.game.id}:0/\n"

    elif 'demand_answer' in kwargs:
        demand_answer = kwargs['demand_answer']
        subject = f"[RPG] Dezyderat {demand_answer.id} [odpowiedź]"
        message = f"Odpowiedź od {demand_answer.author}:\n" \
                  f"{request.get_host()}/contact/demands/detail:{demand_answer.demand.id}/#page-bottom\n"

    else:
        subject = 'Błąd'
        message = f"URL: {request.build_absolute_uri()}\n" \
                  f"kwargs: {kwargs}"

    send_mail(subject, message, sender, receivers)
