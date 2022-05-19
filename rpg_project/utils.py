import os
import re
import time
from functools import wraps
from random import sample

import delegator
from django.apps import apps
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.core.mail import send_mail
from django.shortcuts import redirect
from google.cloud import storage

from django.conf import settings


def upload_to_bucket(destination_path, source_path, bucket_name):
    storage_client = storage.Client.from_service_account_json(
        settings.GOOGLE_APPLICATION_CREDENTIALS)
    bucket = storage_client.get_bucket(bucket_name)
    
    blob = bucket.blob(destination_path)
    blob.upload_from_filename(source_path)
    
    return blob.public_url


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
    

def sample_from_qs(qs, max_size):
    objs_set = set(qs)
    size = max_size if len(objs_set) >= max_size else len(objs_set)
    return sample(objs_set, k=size)


def handle_inform_form(request):
    # Example post data from form
    # dict(request.POST).items() == < QueryDict: {
    #     'csrfmiddlewaretoken': ['KcoYDwb7r86Ll2SdQUNrDCKs...'],
    #     '2': ['on'],
    #     'Location': ['77']
    # } >
    # print(request.POST)
    post_data = dict(request.POST)
    all_models = {model.__name__: model for model in apps.get_models()}
    
    informed_ids = [k for k, v_list in post_data.items() if 'on' in v_list]

    if 'Location' in post_data.keys():
        model = all_models['Location']
        obj = model.objects.get(id=post_data['Location'][0])
        obj.informees.add(*informed_ids)
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
        obj.participants.add(*informed_ids)
        send_emails(request, informed_ids, debate=obj)

    elif 'GameEvent' in post_data.keys():
        model = all_models['GameEvent']
        obj = model.objects.get(id=post_data['GameEvent'][0])
        obj.informees.add(*informed_ids)
        send_emails(request, informed_ids, game_event=obj)

    elif 'HistoryEvent' in post_data.keys():
        model = all_models['HistoryEvent']
        obj = model.objects.get(id=post_data['HistoryEvent'][0])
        obj.informees.add(*informed_ids)
        send_emails(request, informed_ids, history_event=obj)
    
    elif 'Character' in post_data.keys():
        model = all_models['Character']
        obj = model.objects.get(id=post_data['Character'][0])
        obj.informees.add(*informed_ids)
        send_emails(request, informed_ids, character=obj)

    else:
        messages.warning(
            request,
            """Błąd! Prześlij informację MG wraz z opisem czynności
            - kogo o czym informowałeś/do czego dołączałeś.""")


def send_emails(request, profile_ids=None, **kwargs):
    from users.models import Profile
    profile = Profile.objects.get(id=request.session['profile_id'])
    sender = settings.EMAIL_HOST_USER
    receivers = [
        p.user.email
        for p in Profile.active_players.filter(id__in=profile_ids or []).select_related()]
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
        message = f"{profile} dołączył/a Cię do narady '{debate.title}' " \
                  f"w temacie '{debate.topic}'." \
                  f"\nWeź udział w naradzie:" \
                  f"\n{request.build_absolute_uri()}\n"
        messages.info(request, f'Dołączono wybrane Postacie!')

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
        subject = "[RPG] Nowa opowieść o Postaci!"
        message = f"{profile} rozprawia o Postaci '{character}'.\n" \
                  f"Postać została dodana do Twojego Prosoponomikonu: " \
                  f"{request.get_host()}/prosoponomikon/character/{character}/\n"
        messages.info(request, f'Poinformowano wybranych bohaterów!')

    else:
        subject = 'Błąd'
        message = f"URL: {request.build_absolute_uri()}\n" \
                  f"kwargs: {kwargs}"
    
    send_mail(subject, message, sender, receivers)


def formfield_with_cache(field, formfield, request):
    choices = getattr(request, f'_{field}_choices_cache', None)
    if choices is None:
        choices = list(formfield.choices)
        setattr(request, f'_{field}_choices_cache', choices)
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


def backup_db(reason: str):
    date = time.strftime("%Y-%m-%d_%H-%M")
    filename = f"hyllemath_db_{reason}_{date}.json"

    delegator.run(
        f"pg_dump --dbname={settings.GCP_DATABASE_DNS} --format=c --no-owner --no-acl > {filename}")

    upload_to_bucket(
        destination_path=f"backups/{filename}",
        source_path=f"./{filename}",
        bucket_name=settings.GS_BUCKET_NAME)

    return


def update_local_db(reason: str):
    date = time.strftime("%Y-%m-%d_%H-%M")
    filename = f"hyllemath_db_{reason}_{date}.json"
    
    delegator.run(
        f"pg_dump --dbname={settings.GCP_DATABASE_DNS} --format=c --no-owner --no-acl > {filename}")
    delegator.run(
        f"pg_restore --dbname={settings.DEV_DATABASE_DNS} --no-owner --no-acl --clean {filename}",
        block=False)
    
    return

    
def only_game_masters(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        from users.models import Profile
        profile = Profile.objects.get(id=request.session['profile_id'])
        if profile.status == 'gm':
            return function(request, *args, **kwargs)
        else:
            return redirect('users:dupa')
        
    return wrap


def only_game_masters_and_spectators(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        from users.models import Profile
        profile = Profile.objects.get(id=request.session['profile_id'])
        if profile.status in ['gm', 'spectator']:
            return function(request, *args, **kwargs)
        else:
            return redirect('users:dupa')
        
    return wrap


COLORS_LIST = [
    '#000000',
    '#FF0000',
    '#00FF00',
    '#0000FF',
    '#FFFF00',
    '#00FFFF',
    '#FF00FF',
    '#C0C0C0',
    '#808080',
    '#800000',
    '#808000',
    '#008000',
    '#800080',
    '#008080',
    '#000080',
]
COLORS_DICT = {c: c for c in COLORS_LIST}
COLORS_CHOICES = [(c, c) for c in COLORS_LIST]


def transform_to_paragraphs():
    """A function for restoring paragraphs from Django TextField
    and lost by transition to RichTextField
    (in the future should be modified with filter on Statement).
    """
    from communications.models import Statement
    for statement in Statement.objects.all():
        if not statement.text[:2] == '<p>':
            statement.text = '<p>' + statement.text.replace('\r\n\r\n', '</p><p>') + '</p>'
            statement.text = statement.text.replace('\r\n', '</p><p>')
            statement.save()

