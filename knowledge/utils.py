from django.contrib.postgres.expressions import ArraySubquery
from django.db.models import Value, OuterRef
from django.db.models.functions import Concat, JSONObject

from users.models import Profile


def annotate_informables(info_packets, current_profile):
    if info_packets.model.__name__ == 'KnowledgePacket':
        profiles = Profile.active_players.exclude(knowledge_packets=OuterRef('id'))
    elif info_packets.model.__name__ == 'BiographyPacket':
        profiles = Profile.active_players.exclude(biography_packets=OuterRef('id'))
    else:
        return info_packets
        
    informables_subq = profiles.filter(
        character__in=current_profile.character.acquaintances.all()
    ).values(
        json=JSONObject(
            id='id',
            status='status',
            image=JSONObject(url=Concat(Value('/media/'), 'image')),
            character=JSONObject(fullname='character__fullname'),
        )
    )
    return info_packets.annotate(informables=ArraySubquery(informables_subq))



