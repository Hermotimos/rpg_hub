from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render

from knowledge.models import KnowledgePacket
from rpg_project.utils import query_debugger
from rules.models import SkillLevel
from toponomikon.models import GeneralLocation, SpecificLocation

@query_debugger
@login_required
def knowledge_sheet(request):
    profile = request.user.profile
    if profile.character_status == 'gm':
        skills_kn_packets = KnowledgePacket.objects\
            .filter(skill_levels__in=SkillLevel.objects.all())
        gen_locs_kn_packets = KnowledgePacket.objects\
            .filter(general_locations__in=GeneralLocation.objects.all())
        spec_locs_kn_packets = KnowledgePacket.objects\
            .filter(specific_locations__in=SpecificLocation.objects.all())
    else:
        skills_kn_packets = KnowledgePacket.objects\
            .filter(skill_levels__in=profile.character.skill_levels_acquired.all())
        known_gen_locs = (profile.gen_locs_known_directly.all() | profile.gen_locs_known_indirectly.all()).distinct()
        gen_locs_kn_packets = KnowledgePacket.objects.filter(general_locations__in=known_gen_locs)
        known_spec_locs = (profile.spec_locs_known_directly.all() | profile.spec_locs_known_indirectly.all()).distinct()
        spec_locs_kn_packets = KnowledgePacket.objects.filter(specific_locations__in=known_spec_locs)

    context = {
        'page_title': 'Okruchy wiedzy',
        'skills_kn_packets': skills_kn_packets,
        'gen_locs_kn_packets': gen_locs_kn_packets,
        'spec_locs_kn_packets': spec_locs_kn_packets,
    }
    return render(request, 'knowledge/knowledge_sheet.html', context)
