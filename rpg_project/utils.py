import os

from django.conf import settings
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
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
    
    name = name.replace('"', '')
    
    return name


def handle_inform_form(request):
    excluded_apps = ['auth', 'admin', 'sessions', 'contenttypes']
    all_models_in_apps = {
        ct.model_class().__name__: ct.model_class()
        for ct in ContentType.objects.exclude(app_label__in=excluded_apps)
    }
    post_data = dict(request.POST)
    print(post_data)
    # Example post data from form
    # dict(request.POST).items() == < QueryDict: {
    #     'csrfmiddlewaretoken': ['KcoYDwb7r86Ll2SdQUNrDCKs...'],
    #     '2': ['on'],
    #     'Location': ['77']
    # } >

    model = obj = None
    for k, v in post_data.items():
        if k in all_models_in_apps.keys():
            model = all_models_in_apps.get(k)
            obj = model.objects.get(id=v[0])
    if not obj:
        return
    
    sender = EMAIL_HOST_USER
    informed_ids = [k for k, v_list in post_data.items() if 'on' in v_list]
    receivers = [
        p.user.email for p in Profile.objects.filter(id__in=informed_ids)
    ]
    profile = request.user.profile
    if profile.status != 'gm':
        gms = [p.user.email for p in Profile.objects.filter(status='gm')]
        receivers.extend(gms)

    if model.__name__ == 'Location':
        obj.known_indirectly.add(*informed_ids)
        subject = '[RPG] Transfer wiedzy!'
        message = f"{profile} opowiedział/a Ci o miejscu zwanym" \
                  f" '{obj.name}'." \
                  f"\nInformacje zostały zapisane w Twoim Toponomikonie: " \
                  f"\n{request.build_absolute_uri()}\n"
    
    elif model.__name__ == 'KnowledgePacket':
        obj.acquired_by.add(*informed_ids)
        subject = '[RPG] Transfer wiedzy!'
        message = f"{profile} przekazał/a Ci wiedzę nt. '{obj.title}'." \
                  f"\nWiędzę tę możesz odnaleźć w Almanachu pod:" \
                  f" {', '.join(s.name for s in obj.skills.all())}:" \
                  f"\n{request.get_host()}/knowledge/almanac/\n"

    elif model.__name__ == 'Debate':
        obj.known_directly.add(*informed_ids)
        subject = '[RPG] Dołączenie do narady!'
        message = f"{profile} dołączył/a Cię do narady '{obj.name}' " \
                  f"w temacie '{obj.topic}'." \
                  f"\nWeź udział w naradzie:" \
                  f"\n{request.build_absolute_uri()}\n"
       
    elif model.__name__ == 'TimelineEvent':
        obj.known_indirectly.add(*informed_ids)
        subject = "[RPG] Nowa opowieść o wydarzeniach!"
        message = f"{profile} rozprawia o swoich przygodach.\n" \
                  f"'{obj.date()} rozegrało się co następuje...\n " \
                  f"Wydarzenie zostało zapisane w Twoim Kalendarium."

    #  OLD - history app
    elif model.__name__ == 'ChronicleEvent':
        obj.known_indirectly.add(*informed_ids)
        subject = "[RPG] Nowa opowieść o wydarzeniach!"
        message = f"{profile} rozprawia o swoich przygodach.\n" \
                  f"Podczas przygody '{obj.game.title}' " \
                  f"rozegrało się co następuje...\n" \
                  f"Wydarzenie zostało zapisane w Twojej Kronice: " \
                  f"{request.get_host()}/history/chronicle/one-game:{obj.game.id}:0/\n"

    #  NEW - chronicles app
    elif model.__name__ == 'GameEvent':
        obj.known_indirectly.add(*informed_ids)
        subject = "[RPG] Nowa opowieść o wydarzeniach!"
        message = f"{profile} rozprawia o swoich przygodach.\n" \
                  f"Podczas przygody '{obj.game.title}' " \
                  f"rozegrało się co następuje...\n" \
                  f"Wydarzenie zostało zapisane w Twojej Kronice: " \
                  f"{request.get_host()}/chronicles/chronicle/game:{obj.game.id}/\n"
        
    #  NEW - chronicles app
    elif model.__name__ == 'HistoryEvent':
        obj.known_indirectly.add(*informed_ids)
        subject = "[RPG] Nowa opowieść o wydarzeniach historycznych!"
        message = f"{profile} rozprawia o dawnych dziejach.\n" \
                  f"Było to w czasach...\n" \
                  # f"Wydarzenie zostało zapisane w Twojej Kronice: " \
                  # f"{request.get_host()}/chronicles/XXXXXXXX/\n"

    else:
        subject = 'Błąd'
        message = f"URL: {request.build_absolute_uri()}\n" \
                  f"obj: {obj}"
        
    if receivers:
        messages.info(request, f'Poinformowano wybranych bohaterów!')
        
    send_mail(subject, message, sender, receivers)


def send_emails(request, profile_ids, **kwargs):
    profile = request.user.profile
    sender = EMAIL_HOST_USER
    receivers = [
        p.user.email for p in Profile.objects.filter(id__in=profile_ids)
    ]
    if profile.status != 'gm':
        gms = [p.user.email for p in Profile.objects.filter(status='gm')]
        receivers.extend(gms)
    
    # Debates
    if 'remark' in kwargs:
        remark = kwargs['remark']
        debate = remark.debate
        url = f"{request.get_host()}/debates/debate:{debate.id}/" \
              f"#remark-{remark.id}\n"
        new = kwargs['new']
        
        if new == 'topic':
            subject = '[RPG] Nowa narada w nowym temacie!'
            message = f"{profile} włączył/a Cię do nowej narady '{debate}'" \
                      f" w nowym temacie '{debate.topic}'." \
                      f"\nWeź udział w naradzie:\n{url}\n"

        elif new == 'debate':
            subject = '[RPG] Nowa narada!'
            message = f"{profile} włączył/a Cię do nowej narady '{debate}'" \
                      f" w temacie '{debate.topic}'." \
                      f"\nWeź udział w naradzie:\n{url}\n"

        else:  # new == 'remark'
            subject = '[RPG] Wypowiedź w naradzie!'
            message = f"{profile} zabrał/a głos w naradzie '{debate}'" \
                      f" w temacie '{debate.topic}'." \
                      f"\nWeź udział w naradzie:\n{url}\n"
    
    # Demands
    elif 'demand_answer' in kwargs:
        demand_answer = kwargs['demand_answer']
        subject = f"[RPG] Dezyderat {demand_answer.demand.id} [odpowiedź]"
        message = f"Odpowiedź od {demand_answer.author}:\n" \
                  f"{request.get_host()}/contact/demands/detail:{demand_answer.demand.id}/#page-bottom\n"
    
    else:
        subject = 'Błąd'
        message = f"URL: {request.build_absolute_uri()}\n" \
                  f"kwargs: {kwargs}"
    
    send_mail(subject, message, sender, receivers)
