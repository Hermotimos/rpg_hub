import os
import re
import shutil
import time
from random import sample
from functools import wraps

from django.apps import apps
from django.conf import settings
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.core.mail import send_mail
from django.shortcuts import redirect

from rpg_project.settings import EMAIL_HOST_USER


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
    
    def get_valid_name(self, name):
        """Overrides method which would normally replace whitespaces with
        underscores and remove special characters.
            s = str(s).strip().replace(' ', '_')
            return re.sub(r'(?u)[^-\w.]', '', s)
        Modified to leave whitespace and to accept it in regular expressions.
        """
        name = str(name).strip()
        return re.sub(r'(?u)[^-\w.\s]', '', name)
    
    
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


def rid_of_special_chars(text):
    return "".join(
        [ch for ch in text if ch.lower() in 'abcdefghijklmnopqrstuvwxyz']
    )


def sample_from_qs(qs, max_size):
    obj_set = set(qs)
    size = max_size if len(obj_set) >= max_size else len(obj_set)
    return sample(obj_set, k=size)


def handle_inform_form(request):
    # Example post data from form
    # dict(request.POST).items() == < QueryDict: {
    #     'csrfmiddlewaretoken': ['KcoYDwb7r86Ll2SdQUNrDCKs...'],
    #     '2': ['on'],
    #     'Location': ['77']
    # } >
    print(request.POST)
    post_data = dict(request.POST)
    all_models = {model.__name__: model for model in apps.get_models()}
    
    informed_ids = [k for k, v_list in post_data.items() if 'on' in v_list]

    if 'Location' in post_data.keys():
        model = all_models['Location']
        obj = model.objects.get(id=post_data['Location'][0])
        obj.known_indirectly.add(*informed_ids)
        send_emails(request, informed_ids, location=obj)

    elif 'KnowledgePacket' in post_data.keys():
        model = all_models['KnowledgePacket']
        obj = model.objects.get(id=post_data['KnowledgePacket'][0])
        obj.acquired_by.add(*informed_ids)
        send_emails(request, informed_ids, kn_packet=obj)

    elif 'BiographyPacket' in post_data.keys():
        model = all_models['BiographyPacket']
        obj = model.objects.get(id=post_data['BiographyPacket'][0])
        obj.acquired_by.add(*informed_ids)
        send_emails(request, informed_ids, bio_packet=obj)

    elif 'Debate' in post_data.keys():
        model = all_models['Debate']
        obj = model.objects.get(id=post_data['Debate'][0])
        obj.known_directly.add(*informed_ids)
        send_emails(request, informed_ids, debate=obj)

    elif 'GameEvent' in post_data.keys():
        model = all_models['GameEvent']
        obj = model.objects.get(id=post_data['GameEvent'][0])
        obj.known_indirectly.add(*informed_ids)
        send_emails(request, informed_ids, game_event=obj)

    elif 'HistoryEvent' in post_data.keys():
        model = all_models['HistoryEvent']
        obj = model.objects.get(id=post_data['HistoryEvent'][0])
        obj.known_indirectly.add(*informed_ids)
        send_emails(request, informed_ids, history_event=obj)
    
    elif 'Character' in post_data.keys():
        model = all_models['Character']
        obj = model.objects.get(id=post_data['Character'][0])
        obj.known_indirectly.add(*informed_ids)
        send_emails(request, informed_ids, character=obj)

    else:
        messages.warning(
            request,
            """Błąd! Prześlij informację MG wraz z opisem czynności
            - kogo o czym informowałeś/do czego dołączałeś.""")


def send_emails(request, profile_ids=None, **kwargs):
    from users.models import Profile
    profile = request.user.profile
    sender = EMAIL_HOST_USER
    receivers = [
        p.user.email
        for p in Profile.objects.filter(id__in=profile_ids or []).select_related()]
    if profile.status != 'gm':
        gms = [
            p.user.email
            for p in Profile.objects.filter(status='gm').select_related()]
        receivers.extend(gms)

    # DEBATES
    
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
    
    # DEMANDS
    elif 'demand' in kwargs:
        
        # Demand done/undone
        if 'is_done' in kwargs:
            demand = kwargs['demand']
            is_done = kwargs['is_done']
            status = "zrobiony" if is_done else "NIE-zrobiony!"
            subject = f"[RPG] Dezyderat nr {demand.id} [{status}]"
            message = f"{profile} oznaczył dezyderat jako '{status}'.\n" \
                      f"Dezyderat:\n" \
                      f"{request.get_host()}/contact/demands/detail:{demand.id}/\n\n"
            messages.info(request, f"Oznaczono jako {status}!")
            
        # Demand create
        else:
            demand = kwargs['demand']
            subject = f"[RPG] Dezyderat {demand.id} [nowy]"
            message = f"{demand.author} wysłał Ci Dezyderat:\n" \
                      f"{request.get_host()}/contact/demands/detail:{demand.id}/\n\n"
            messages.info(request, 'Dezyderat został wysłany!')
        
    # DEMAND ANSWER
    elif 'demand_answer' in kwargs:
        demand_answer = kwargs['demand_answer']
        subject = f"[RPG] Dezyderat {demand_answer.demand.id} [odpowiedź]"
        message = f"Odpowiedź od {demand_answer.author}:\n" \
                  f"{request.get_host()}/contact/demands/detail:{demand_answer.demand.id}/#page-bottom\n"
        messages.info(request, 'Dodano odpowiedź!')
   
    # PLAN (created)
    elif 'plan_created' in kwargs:
        plan = kwargs['plan_created']
        subject = f"[RPG] Info o planach od {profile}"
        message = f"{profile} informuje o swoich planach:\n\n{plan.text}\n" \
                  f"{request.get_host()}/contact/plans/for-gm/\n\n"
        messages.info(request, f'Plan został zapisany!')

    # PLAN (modified)
    elif 'plan_modified' in kwargs:
        plan = kwargs['plan_modified']
        subject = f"[RPG] Info o zmianie planów od {profile}"
        message = f"{profile} informuje o zmianie planów:\n\n{plan.text}\n" \
                  f"{request.get_host()}/contact/plans/for-gm/\n\n"
        messages.info(request, 'Zmodyfikowano plan!')

    # ------------------------------------------------------------------------
    # ------------------------- INFORM FEATURE -------------------------------
    # ------------------------------------------------------------------------

    # LOCATION
    elif 'location' in kwargs:
        location = kwargs['location']
        subject = '[RPG] Transfer wiedzy!'
        message = f"{profile} opowiedział/a Ci o miejscu zwanym" \
                  f" '{location.name}'." \
                  f"\nInformacje zostały zapisane w Twoim Toponomikonie: " \
                  f"\n{request.build_absolute_uri()}\n"
        messages.info(request, f'Poinformowano wybranych bohaterów!')

    # KNOWLEDGE PACKET
    elif 'kn_packet' in kwargs:
        kn_packet = kwargs['kn_packet']
        subject = '[RPG] Transfer wiedzy!'
        message = f"{profile} przekazał/a Ci wiedzę nt. '{kn_packet.title}'." \
                  f"\nWiędzę tę możesz odnaleźć w Almanachu pod:" \
                  f" {', '.join(s.name for s in kn_packet.skills.all())}:" \
                  f"\n{request.get_host()}/knowledge/almanac/\n"
        messages.info(request, f'Poinformowano wybranych bohaterów!')

    # BIOGRAPHY PACKET
    elif 'bio_packet' in kwargs:
        bio_packet = kwargs['bio_packet']
        subject = '[RPG] Transfer wiedzy!'
        message = f"{profile} przekazał/a Ci wiedzę nt. '{bio_packet.title}'." \
                  f"\nWiędzę tę możesz odnaleźć w Prosoponomikonie pod:" \
                  f" {bio_packet.characters.all().first().name}:" \
                  f"\n{request.get_host()}/prosoponomikon/character/{bio_packet.characters.all().first().id}/\n"
        messages.info(request, f'Poinformowano wybranych bohaterów!')

    # DEBATE
    elif 'debate' in kwargs:
        debate = kwargs['debate']
        subject = '[RPG] Dołączenie do narady!'
        message = f"{profile} dołączył/a Cię do narady '{debate.name}' " \
                  f"w temacie '{debate.topic}'." \
                  f"\nWeź udział w naradzie:" \
                  f"\n{request.build_absolute_uri()}\n"
        messages.info(request, f'Dołączono wybrane postacie!')

    # GAME EVENT
    elif 'game_event' in kwargs:
        game_event = kwargs['game_event']
        subject = "[RPG] Nowa opowieść o wydarzeniach!"
        message = f"{profile} rozprawia o przygodzie '{game_event.game.title}'.\n" \
                  f"Wydarzenie zostało zapisane w Twojej Kronice: " \
                  f"{request.get_host()}/chronicles/chronicle/game:{game_event.game.id}/\n"
        messages.info(request, f'Poinformowano wybranych bohaterów!')

    # HISTORY EVENT
    elif 'history_event' in kwargs:
        history_event = kwargs['history_event']
        subject = "[RPG] Nowa opowieść o wydarzeniach historycznych!"
        message = f"{profile} rozprawia o dawnych dziejach.\n" \
                  f"Było to w czasach...\n" \
                  # f"Wydarzenie zostało zapisane w Twojej Kronice: " \
                  # f"{request.get_host()}/chronicles/XXXXXXXX/\n"
        messages.info(request, f'Poinformowano wybranych bohaterów!')

    # CHARACTER
    elif 'character' in kwargs:
        character = kwargs['character']
        subject = "[RPG] Nowa opowieść o postaci!"
        message = f"{profile} rozprawia o postaci '{character}'.\n" \
                  f"Postać została dodana do Twojego Prosoponomikonu: " \
                  f"{request.get_host()}/prosoponomikon/character/{character}/\n"
        messages.info(request, f'Poinformowano wybranych bohaterów!')

    else:
        subject = 'Błąd'
        message = f"URL: {request.build_absolute_uri()}\n" \
                  f"kwargs: {kwargs}"
    
    send_mail(subject, message, sender, receivers)


def formfield_for_dbfield_cached(cls, db_field, fields, **kwargs):
    """An abstraction to override formfield_for_dbfield inside any
    admin.ModelAdmin or admin.TabularInline subclass (others not tested yet).
    The original post has a different trick for inlines, but this works better.
    
    https://blog.ionelmc.ro/2012/01/19/tweaks-for-making-django-admin-faster/
    If you have foreign keys in list_editable django will make 1 database query
    for each item in the changelist.
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        request = kwargs['request']
        formfield = super().formfield_for_dbfield(db_field, **kwargs)
        fields = [
            'affix_group',
            'auxiliary_group',
        ]
        for field in fields:
            if db_field.name == field:
                choices = getattr(request, f'_{field}_choices_cache', None)
                if choices is None:
                    choices = list(formfield.choices)
                    setattr(request, f'_{field}_choices_cache', choices)
                formfield.choices = choices
        return formfield

    Greatly reduces queries in main view, doubles in detail view: trade-off ok.
    """
    request = kwargs['request']
    formfield = super(type(cls), cls).formfield_for_dbfield(db_field, **kwargs)
    for f in fields:
        if db_field.name == f:
            choices = getattr(request, f'_{f}_choices_cache', None)
            if choices is None:
                choices = list(formfield.choices)
                setattr(request, f'_{f}_choices_cache', choices)
            formfield.choices = choices
    return formfield


def update_rel_objs(instance, RelModel, rel_queryset, rel_name: str):
    """A helper function to use in AdminForm's, where related objects are
    presented as a virtual field, in order to facilitate updates.
    """
    for obj in RelModel.objects.all():
        if obj.id in [obj.id for obj in rel_queryset]:
            exec(f"obj.{rel_name}.add(instance)")
        else:
            exec(f"obj.{rel_name}.remove(instance)")


def backup_db(reason=""):
    cwd = os.getcwd()
    date = time.strftime("%Y-%m-%d_%H.%M")
    reason = f"_{reason}"
    shutil.copy2(f"{cwd}/db.sqlite3", f"{cwd}/db_copy_{date}{reason}.sqlite3")


def only_game_masters(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.user.profile.status == 'gm':
            return function(request, *args, **kwargs)
        else:
            return redirect('home:dupa')
        
    return wrap
