from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from knowledge.models import KnowledgePacket
from rpg_project.utils import query_debugger


@query_debugger
@login_required
def knowledge_sheet(request):
    profile = request.user.profile
    if profile.character_status == 'gm':
        skills_kn_packets = KnowledgePacket.objects.filter(skill_levels=True)
        # gen_locs_kn_packets = GeneralLocation.objects.all()
        # spec_locs_kn_packets = SpecificLocation.objects.all()
    else:
        pass
        skills_kn_packets = []

    context = {
        'page_title': 'Okruchy wiedzy',
        'skills_kn_packets': skills_kn_packets,
    }
    return render(request, 'characters/knowledge_sheet.html', context)
