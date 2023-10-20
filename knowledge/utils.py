from django.conf import settings
from django.contrib.postgres.expressions import ArraySubquery
from django.db.models import Value, OuterRef, Case, When, Q
from django.db.models.functions import Concat, JSONObject

from users.models import Profile


def annotate_informables(info_packets, current_profile):
    if info_packets.model.__name__ in ['KnowledgePacket', 'BiographyPacket']:
        acquaintanceships = current_profile.character.acquaintanceships().filter(
            known_character__profile__in=Profile.active_players.all()
        ).exclude(
            known_character__profile__knowledge_packets=OuterRef('id')
        )
    else:
        return info_packets

    # TODO temp 'Ilen z Astinary, Alora z Astinary'
    # hide Davos from Ilen and Alora
    if current_profile.id in [5, 6]:
        acquaintanceships = acquaintanceships.exclude(known_character__profile__id=3)
    # vice versa
    if current_profile.id == 3:
        acquaintanceships = acquaintanceships.exclude(known_character__profile__id__in=[5, 6])
    # TODO end temp

    informables_subq = acquaintanceships.values(
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
    return info_packets.annotate(informables=ArraySubquery(informables_subq))
