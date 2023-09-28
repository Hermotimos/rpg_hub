from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Case, OuterRef, Prefetch, Q, Value, When
from django.db.models.functions import Concat, JSONObject
from django.http import JsonResponse
from django.shortcuts import redirect, render

from imaginarion.models import Picture, PictureImage, PictureSet
from knowledge.forms import PlayerKnPacketForm
from knowledge.models import KnowledgePacket
from knowledge.utils import annotate_informables
from rpg_project.utils import auth_profile, handle_inform_form
from rules.models import Skill
from users.models import Profile


@login_required
@auth_profile(['all'])
def almanac_view(request):
    current_profile = request.current_profile

    knowledge_packets = KnowledgePacket.objects.select_related('author')
    knowledge_packets = annotate_informables(knowledge_packets, current_profile)
    if not current_profile.can_view_all:
        knowledge_packets = knowledge_packets.filter(acquired_by=current_profile)

    skills = Skill.objects.filter(knowledge_packets__in=knowledge_packets)
    skills = skills.prefetch_related(
        Prefetch('knowledge_packets', queryset=knowledge_packets),
        'knowledge_packets__picture_sets__pictures',
        'knowledge_packets__references')

    if request.method == 'POST':
        handle_inform_form(request)

    context = {
        'page_title': 'Almanach',
        'skills': skills.distinct(),
    }
    return render(request, 'knowledge/skills_with_kn_packets.html', context)


@login_required
@auth_profile(['all'])
def kn_packet_form_view(request, kn_packet_id):
    current_profile = request.current_profile

    kn_packet = KnowledgePacket.objects.filter(id=kn_packet_id).first()
    form = PlayerKnPacketForm(
        data=request.POST or None,
        files=request.FILES or None,
        instance=kn_packet,
        current_profile=current_profile)

    if form.is_valid():
        if current_profile.status == 'gm':
            kn_packet = form.save()
        else:
            kn_packet = form.save(commit=False)
            kn_packet.author = current_profile
            kn_packet.save()
            kn_packet.acquired_by.add(current_profile)
            kn_packet.skills.set(form.cleaned_data['skills'])

            pictures = [v for k, v in form.cleaned_data.items()
                        if 'picture' in k and v is not None]

            new_pictures = []
            for cnt, picture in enumerate(pictures, 1):
                description = (form.cleaned_data[f'descr_{cnt}']
                               or f"{kn_packet.title}")
                pic_img = PictureImage.objects.create(
                    image=picture,
                    description=description)
                pic = Picture.objects.create(
                    image=pic_img,
                    type='players-notes',
                    description=description)
                new_pictures.append(pic)

            if new_pictures:
                now = datetime.now().strftime("%Y-%d-%m %H:%M:%S")
                title = f"""
                    KnowledgePacket: '{kn_packet.title}'
                    [Autor: {current_profile.character.first_name} - {now}]
                """
                new_picture_set = PictureSet.objects.create(title=title)
                new_picture_set.pictures.set(new_pictures)
                kn_packet.picture_sets.add(new_picture_set)

        for location in form.cleaned_data['locations']:
            location.knowledge_packets.add(kn_packet)

        messages.success(
            request, f'Zapisano pakiet wiedzy "{kn_packet.title}"!')
        return redirect('knowledge:almanac')
    else:
        messages.warning(request, form.errors)

    context = {
        'page_title': kn_packet.title if kn_packet else 'Nowy pakiet wiedzy',
        'form': form,
    }
    if not kn_packet_id or current_profile.status == 'gm' \
            or current_profile.knowledge_packets.filter(id=kn_packet_id):
        return render(request, '_form.html', context)
    else:
        return redirect('users:dupa')



def knowledge_packet_informables(request, knowledge_packet_id: int, current_profile_id: int):
    current_profile = Profile.objects.get(id=current_profile_id)

    knowledge_packet = KnowledgePacket.objects.get(id=knowledge_packet_id)

    acquaintanceships = current_profile.character.acquaintanceships().filter(
        known_character__profile__in=Profile.active_players.all()
    ).exclude(
        known_character__profile__knowledge_packets=OuterRef('id')      # TODO co to ????
    )

    # TODO temp 'Ilen z Astinary, Alora z Astinary'
    # hide Davos from Ilen and Alora
    if current_profile_id in [5, 6]:
        acquaintanceships = acquaintanceships.exclude(known_character__profile__id=3)
    # vice versa
    if current_profile_id == 3:
        acquaintanceships = acquaintanceships.exclude(known_character__profile__id__in=[5, 6])
    # TODO end temp

    # Exclude Acquaintanceship-s leading to Profiles who have already acquired
    acquaintanceships = acquaintanceships.exclude(
        known_character__profile__id__in=knowledge_packet.acquired_by.all())

    informables = acquaintanceships.values(
        json=JSONObject(
            id='known_character__profile__id',
            status='known_character__profile__status',
            known_character=JSONObject(
                fullname='known_character__fullname',
                profile=JSONObject(
                    id='known_character__profile__id',
                    is_alive='known_character__profile__is_alive',
                    image=JSONObject(
                        url=Concat(Value(settings.MEDIA_URL), 'known_character__profile__image')
                    ),
                )
            ),
            is_direct='is_direct',
            knows_if_dead='knows_if_dead',
            knows_as_name='knows_as_name',
            knows_as_image=Case(
                When(~Q(knows_as_image=''), then=JSONObject(url=Concat(Value(settings.MEDIA_URL), 'knows_as_image'))),
                default=None,
            ),
        )
    )
    return JsonResponse(
        {
            "informables": list(informables.values()),
        }
    )