import os
import random
import re
import time
import uuid
from functools import wraps

import delegator
from django.apps import apps
from django.conf import settings
from django.contrib import auth, messages
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.core.mail import send_mail
from django.db.models import CharField, Func
from django.shortcuts import redirect
from PIL import Image


def sample_from_qs(qs, max_size):
    objs = list(qs)
    size = max_size if len(objs) >= max_size else len(objs)
    return random.sample(objs, k=size)


def handle_inform_form(request):
    from prosoponomikon.models import Acquaintanceship, Character

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

    elif 'Acquaintanceship' in post_data.keys():
        model = all_models['Acquaintanceship']
        obj = model.objects.get(id=post_data['Acquaintanceship'][0])
        for character in Character.objects.filter(profile_id__in=informed_ids):
            Acquaintanceship.objects.create(
                knowing_character=character,
                known_character=obj.known_character,
                is_direct=False,
                knows_if_dead=obj.knows_if_dead,
                knows_as_name=obj.knows_as_name,
                knows_as_description=obj.knows_as_description,
                knows_as_image=obj.knows_as_image)
        send_emails(request, informed_ids, acquaintanceship=obj)

    else:
        messages.warning(
            request,
            """Błąd! Prześlij MG informację z opisem czynności
            - kogo o czym informowałeś/do czego dołączałeś.""")


def send_emails(request, profile_ids=None, **kwargs):
    from users.models import Profile
    current_profile = Profile.objects.get(id=request.session['profile_id'])
    sender = settings.EMAIL_HOST_USER
    receivers = []

    # Send emails only in production
    if settings.EMAIL_SEND_ALLOWED:
        receivers = [
            p.user.email
            for p in Profile.players.filter(id__in=profile_ids or []).select_related()]
    if current_profile.status != 'gm':
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
            message = f"{current_profile} włączył/a Cię do nowej narady '{debate}'" \
                      f" w nowym temacie '{debate.topic}'." \
                      f"\nWeź udział w naradzie:\n{url}\n"

        elif new == 'debate':
            subject = '[RPG] Nowa narada!'
            message = f"{current_profile} włączył/a Cię do nowej narady '{debate}'" \
                      f" w temacie '{debate.topic}'." \
                      f"\nWeź udział w naradzie:\n{url}\n"

        else:  # new == 'remark'
            subject = '[RPG] Wypowiedź w naradzie!'
            message = f"{current_profile} zabrał/a głos w naradzie '{debate}'" \
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
            message = f"{current_profile} oznaczył dezyderat jako '{status}'.\n" \
                      f"Dezyderat:\n" \
                      f"{request.get_host()}/contact/demands/detail:{demand.id}/\n\n"
            messages.info(request, f"Oznaczono jako {status}!")

        # Demand create
        else:
            demand = kwargs['demand']
            subject = f"[RPG] Dezyderat {demand.id} [nowy]"
            message = f"Nowy Dezyderat od: {demand.author}\n" \
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
        subject = f"[RPG] Info o planach od {current_profile}"
        message = f"{current_profile} informuje o swoich planach:\n\n{plan.text}\n" \
                  f"{request.get_host()}/contact/plans/for-gm/\n\n"
        messages.info(request, f'Plan został zapisany!')

    # PLAN (modified)
    elif 'plan_modified' in kwargs:
        plan = kwargs['plan_modified']
        subject = f"[RPG] Info o zmianie planów od {current_profile}"
        message = f"{current_profile} informuje o zmianie planów:\n\n{plan.text}\n" \
                  f"{request.get_host()}/contact/plans/for-gm/\n\n"
        messages.info(request, 'Zmodyfikowano plan!')

    # ------------------------------------------------------------------------
    # ------------------------- INFORM FEATURE -------------------------------
    # ------------------------------------------------------------------------

    # LOCATION
    elif 'location' in kwargs:
        location = kwargs['location']
        subject = '[RPG] Transfer wiedzy!'
        message = f"{current_profile} opowiedział/a Ci o miejscu zwanym" \
                  f" '{location.name}'." \
                  f"\nInformacje zostały zapisane w Twoim Toponomikonie: " \
                  f"\n{request.build_absolute_uri()}\n"
        messages.info(request, f'Poinformowano wybrane Postacie!')

    # KNOWLEDGE PACKET
    elif 'kn_packet' in kwargs:
        kn_packet = kwargs['kn_packet']
        subject = '[RPG] Transfer wiedzy!'
        message = f"{current_profile} przekazał/a Ci wiedzę nt. '{kn_packet.title}'." \
                  f"\nWiędzę tę możesz odnaleźć w Almanachu pod:" \
                  f" {', '.join(s.name for s in kn_packet.skills.all())}:" \
                  f"\n{request.get_host()}/knowledge/almanac/\n"
        messages.info(request, f'Poinformowano wybrane Postacie!')

    # BIOGRAPHY PACKET
    elif 'bio_packet' in kwargs:
        bio_packet = kwargs['bio_packet']
        subject = '[RPG] Transfer wiedzy!'
        message = f"{current_profile} przekazał/a Ci wiedzę nt. '{bio_packet.title}'." \
                  f"\nWiędzę tę możesz odnaleźć w Prosoponomikonie pod:" \
                  f" {bio_packet.characters.first().fullname}:" \
                  f"\n{request.get_host()}/prosoponomikon/character/{bio_packet.characters.all().first().id}/\n"
        messages.info(request, f'Poinformowano wybrane Postacie!')

    # DEBATE
    elif 'debate' in kwargs:
        debate = kwargs['debate']
        subject = '[RPG] Dołączenie do narady!'
        message = f"{current_profile} dołączył/a Cię do narady '{debate.title}' " \
                  f"w temacie '{debate.topic}'." \
                  f"\nWeź udział w naradzie:" \
                  f"\n{request.build_absolute_uri()}\n"
        messages.info(request, f'Dołączono wybrane Postacie!')

    # GAME EVENT
    elif 'game_event' in kwargs:
        game_event = kwargs['game_event']
        subject = "[RPG] Nowa opowieść o wydarzeniach!"
        message = f"{current_profile} rozprawia o przygodzie '{game_event.game.title}'.\n" \
                  f"Wydarzenie zostało zapisane w Twojej Kronice: " \
                  f"{request.get_host()}/chronicles/chronicle/game:{game_event.game.id}/\n"
        messages.info(request, f'Poinformowano wybrane Postacie!')

    # HISTORY EVENT
    elif 'history_event' in kwargs:
        history_event = kwargs['history_event']
        subject = "[RPG] Nowa opowieść o wydarzeniach historycznych!"
        message = f"{current_profile} rozprawia o dawnych dziejach.\n" \
                  f"Było to w czasach...\n" \
                  # f"Wydarzenie zostało zapisane w Twojej Kronice: " \
                  # f"{request.get_host()}/chronicles/XXXXXXXX/\n"
        messages.info(request, f'Poinformowano wybrane Postacie!')

    # CHARACTER
    elif 'acquaintanceship' in kwargs:
        acquaintanceship = kwargs['acquaintanceship']
        subject = "[RPG] Nowa opowieść o Postaci!"
        message = f"{current_profile} rozprawia o Postaci " \
                  f"'{acquaintanceship.knows_as_name or acquaintanceship.known_character.fullname}'.\n" \
                  f"Postać została dodana do Twojego Prosoponomikonu: " \
                  f"{acquaintanceship.known_character.get_absolute_url()}\n"
        messages.info(request, f'Poinformowano wybrane Postacie!')

    else:
        subject = 'Błąd'
        message = f"URL: {request.build_absolute_uri()}\n" \
                  f"kwargs: {kwargs}"

    send_mail(subject, message, sender, receivers)


# -----------------------------------------------------------------------------


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


# -----------------------------------------------------------------------------


def backup_db():
    date = time.strftime("%Y-%m-%d_%H-%M")
    filename = f"_db_saves/prod_hyllemath_{date}.json"

    delegator.run(
        f"pg_dump --dbname={settings.DEV_DATABASE_DNS} --format=c --no-owner --no-acl > {filename}")


def update_db(reason: str, src: str, dst: str):
    date = time.strftime("%Y-%m-%d_%H-%M")

    # Backup dst db
    if reason == "prod":
        backup_name = f"_db_saves/prod_hyllemath_{date}.json"
    else:
        backup_name = f"_db_saves/dev_hyllemath_{date}.json"
    delegator.run(
        f"pg_dump --dbname={dst} --format=c --no-owner --no-acl > {backup_name}")

    # Create tmp dump file used in pg_restore
    filename = f"tmp_hyllemath_{date}.json"
    delegator.run(
        f"pg_dump --dbname={src} --format=c --no-owner --no-acl > {filename}")

    # Clean-up dst db ("pg_restore --clean" sometimes fails to drop tables):
    reset_db_sql = """
        DROP SCHEMA public CASCADE;
        CREATE SCHEMA public;
        GRANT ALL ON SCHEMA public TO postgres;
        GRANT ALL ON SCHEMA public TO public;
    """
    delegator.run(f"psql --dbname={dst} {reset_db_sql}")

    # Update dst db
    delegator.run(
        f"pg_restore --dbname={dst} --no-owner --no-acl --clean {filename}",
        block=False)

    # Remove tmp_hyllemath file
    delegator.run(f"rm {filename}")


# -----------------------------------------------------------------------------


def only_game_masters(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        from users.models import Profile
        current_profile = Profile.objects.get(id=request.session['profile_id'])
        if current_profile.status == 'gm':
            return function(request, *args, **kwargs)
        else:
            return redirect('users:dupa')

    return wrap


def only_game_masters_and_spectators(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        from users.models import Profile
        current_profile = Profile.objects.get(id=request.session['profile_id'])
        if current_profile.status in ['gm', 'spectator']:
            return function(request, *args, **kwargs)
        else:
            return redirect('users:dupa')

    return wrap


def auth_profile(allowed_status: list):
    """Check User's Profile authorization to use a view.
    Log out user if there's a NoReverseMatch exception due to problems with
    session['profile_id'] with URL of 'prosoponomikon:character' view.
    If Profile is authorized to use the view, provide request with
    'current_profile' attribute that can be accessed in vies and templates.
    """
    from users.models import Profile

    def wrapper(view_func):

        def wrapped(request, *args, **kwargs):
            try:
                current_profile = Profile.objects.get(id=request.session.get('profile_id'))
            except Profile.DoesNotExist:
                current_profile = None

            if not current_profile or not current_profile.character.id:
                auth.logout(request)
                messages.warning(request, 'Wystąpił problem z uwierzytelnieniem sesji użytkownika. Zaloguj się ponownie!')
                return redirect('users:logout')

            request.current_profile = current_profile

            if 'all' in allowed_status or current_profile.status in allowed_status:
                return view_func(request, *args, **kwargs)
            return redirect('users:dupa')

        return wrapped

    return wrapper


# -----------------------------------------------------------------------------

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


# -----------------------------------------------------------------------------


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


def get_obj_or_none(classmodel, **kwargs):
    """Analogue to get_obj_or_404 to automate exception handling."""
    try:
        return classmodel.objects.get(**kwargs)
    except classmodel.DoesNotExist:
        return None


# -----------------------------------------------------------------------------


class OrderByPolish(Func):
    """A Func object for ordering by Polish alphabet characters."""
    function = 'COLLATE'

    def as_sql(self, compiler, connection, **extra_context):
        return super().as_sql(
            compiler, connection,
            function='pl-PL-x-icu',
            template='(%(expressions)s) COLLATE "%(function)s"',
            **extra_context)

# -----------------------------------------------------------------------------


class ColorSchemeChoiceField(CharField):
    COLOR_SCHEME = [
        ('light', 'light'),
        ('dark', 'dark'),
        ('info', 'info'),
        ('warning', 'warning'),
        ('danger', 'danger'),
    ]

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 9
        kwargs['default'] = 'light'
        kwargs['choices'] = self.COLOR_SCHEME
        super().__init__(*args, **kwargs)


def determine_icons_color(profile_obj):

    def luminance(pixel):
        return 0.299 * pixel[0] + 0.587 * pixel[1] + 0.114 * pixel[2]

    def is_similar(pixel):
        return 1 if abs(luminance(pixel) - luminance(criterion)) < threshold else 0

    sample_size = 1000
    criterion = (250, 250, 250)
    threshold = 30

    im = Image.open(profile_obj.image)
    im_part = im.crop((0, 0, round(im.width * 0.1), round(im.height * 0.4)))
    pixels = list(im_part.getdata())

    similarity = sum(is_similar(s) for s in random.sample(pixels, sample_size)) / sample_size

    return "dark" if similarity > 0.5 else "light"


# -----------------------------------------------------------------------------


def ensure_unique_filename(filename: str):
    """If filename doesn't contain UUID, add it as postfix."""
    uuid_pattern = r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}"
    match = re.search(uuid_pattern, filename)
    if match:
        return filename

    uuid_postfix = str(uuid.uuid4())
    fname, extension = os.path.splitext(filename)
    return f"{fname}-{uuid_postfix}{extension}"


# -----------------------------------------------------------------------------


def clear_cache(cachename: str, vary_on_list: list[list]):
    """
    Remove cache by its name for all Users.

    Ex.
    {% cache 604800 navbar request.current_profile.user.id %}
    cache name = 'navbar'
    cache vary = request.current_profile.user.id

    This cache named 'navbar' uses User.id as Vary parameter.
    Thus User.id has to be provided to find cache keys.

    """

    def _print_cache_keys():
        mycache = cache._cache
        for key in mycache.keys():
            print(key)

    # _print_cache_keys()
    print(vary_on_list)
    for vary_on in vary_on_list:
        cache_key = make_template_fragment_key(cachename, vary_on)
        print(cache_key, '---', cache.delete(cache_key))
        cache.delete(cache_key)


def profiles_to_userids(profiles) -> list[int]:
    """Get distinct User.id-s for the list of profiles."""
    return list(
        profiles.order_by('user').distinct('user').values_list('user', flat=True)
    )


# -----------------------------------------------------------------------------
