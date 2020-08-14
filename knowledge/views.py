from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch, Q, ExpressionWrapper, BooleanField
from django.shortcuts import render

from knowledge.models import KnowledgePacket
from rpg_project.utils import handle_inform_form
from rules.models import SkillLevel, Skill


def custom_sort(skills_qs):
    # Custom sorting to bring specific skills to the front of the queryset:
    # Source: https://stackoverflow.com/questions/11622501/order-query-results-by-startswith-match
    
    search_terms = [
        'Teolog',
    ]
    for search_term in search_terms:
        # Use expression evaluation to annotate objects; order by annotation
        expression = Q(name__startswith=search_term)
        is_match = ExpressionWrapper(expression, output_field=BooleanField())
        skills_qs = skills_qs.annotate(annotation=is_match)
        # Order by the annotated field in reverse, so `True` is first (0 < 1).
        skills_qs = skills_qs.order_by('-annotation', 'name')
    
    return skills_qs


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
    skills = custom_sort(skills)

    if request.method == 'POST':
        handle_inform_form(request)
    
    context = {
        'page_title': page_title,
        'skills': skills,
    }
    return render(request, 'knowledge/skills_with_kn_packets.html', context)
