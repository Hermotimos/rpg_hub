from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from knowledge.models import KnowledgePacket
from rpg_project.utils import query_debugger
from rules.models import SkillLevel
from toponomikon.models import GeneralLocation, SpecificLocation


@query_debugger
@login_required
def knowledge_sheet_view(request):
    profile = request.user.profile
    if profile.character_status == 'gm':
        skills_kn_packets = KnowledgePacket.objects\
            .filter(skill_levels__in=SkillLevel.objects.all())\
            .prefetch_related('pictures')
        toponomikon_kn_packets = (
                KnowledgePacket.objects.filter(general_locations__in=GeneralLocation.objects.all()) | \
                KnowledgePacket.objects.filter(specific_locations__in=SpecificLocation.objects.all())
        )\
            .distinct()\
            .prefetch_related('pictures')
    else:
        skills_kn_packets = KnowledgePacket.objects\
            .filter(skill_levels__in=profile.character.skill_levels_acquired.all())\
            .prefetch_related('pictures')

        known_gen_locs = (profile.gen_locs_known_directly.all() | profile.gen_locs_known_indirectly.all()).distinct()
        known_spec_locs = (profile.spec_locs_known_directly.all() | profile.spec_locs_known_indirectly.all()).distinct()
        toponomikon_kn_packets = (
                KnowledgePacket.objects.filter(general_locations__in=known_gen_locs) |
                KnowledgePacket.objects.filter(specific_locations__in=known_spec_locs)
        )\
            .distinct()\
            .prefetch_related('pictures')

    context = {
        'page_title': 'Okruchy wiedzy',
        'skills_kn_packets': skills_kn_packets,
        'toponomikon_kn_packets': toponomikon_kn_packets,
    }
    return render(request, 'knowledge/knowledge_sheet.html', context)
