from django.apps import apps
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.shortcuts import render

from knowledge.models import KnowledgePacket
from rpg_project.utils import handle_inform_form
from rules.models import SkillLevel, Skill


@login_required
def knowledge_packets_in_skills_view(request, model_name):
    profile = request.user.profile
    skill_model = apps.get_app_config('rules').get_model(model_name)
    skills = skill_model.objects.all()

    # Filter skills queryset according to possible proxy usage
    skill_proxies = [
        m for m in apps.get_app_config('rules').get_models()
        if issubclass(m, Skill) and m.__name__ != Skill.__name__
    ]
    page_title = skill_model._meta.verbose_name
    if skill_model == Skill:
        page_title = 'Almanach'
        for proxy in skill_proxies:
            skills = skills.exclude(id__in=proxy.objects.all())

    # Filter skills queryset according to profile's permissions
    kn_packets = KnowledgePacket.objects.all()
    skill_levels = SkillLevel.objects.all()
    if profile.status != 'gm':
        kn_packets = kn_packets.filter(acquired_by=profile)
        skill_levels = skill_levels.filter(acquired_by=profile)
        
    skills = skills.filter(knowledge_packets__in=kn_packets)
    skills = skills.prefetch_related(
        Prefetch('knowledge_packets', queryset=kn_packets),
        Prefetch('skill_levels', queryset=skill_levels),
        'knowledge_packets__pictures',
    )
    skills = skills.distinct()

    if request.method == 'POST':
        handle_inform_form(request)
    
    context = {
        'page_title': page_title,
        'skills': skills,
    }
    return render(request, 'knowledge/skills_with_kn_packets.html', context)
