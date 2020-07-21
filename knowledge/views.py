from django.apps import apps
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch, Q, ExpressionWrapper, BooleanField
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views import View

from knowledge.models import KnowledgePacket
from rpg_project.utils import send_emails
from rules.models import SkillLevel, Skill, TheologySkill, BooksSkill


def prepare_skills(profile, skill_model_name):
    skill_model = apps.get_app_config('rules').get_model(skill_model_name)
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
    if profile.status == 'gm':
        kn_packets = KnowledgePacket.objects.all()
        skill_levels = SkillLevel.objects.all()
    else:
        kn_packets = profile.knowledge_packets.all()
        skill_levels = SkillLevel.objects.filter(acquired_by=profile)
        
    skills = skills.filter(knowledge_packets__in=kn_packets)
    skills = skills.prefetch_related(
        Prefetch('knowledge_packets', queryset=kn_packets),
        Prefetch('skill_levels', queryset=skill_levels),
        'knowledge_packets__pictures',
    )
    skills = skills.distinct()
    
    return page_title, skills


@login_required
def skills_view(request, skill_model):
    page_title, skills = prepare_skills(request.user.profile, skill_model)
    
    # INFORM FORM
    if request.method == 'POST' and 'kn_packet' in request.POST:
        # dict(request.POST).items() == < QueryDict: {
        #     'csrfmiddlewaretoken': ['KcoYDwb7r86Ll2SdQUNrDCKs...'],
        #     '2': ['on'],
        #     'kn_packet': ['38']
        # } >
        data = dict(request.POST)
        informed_ids = [k for k, v_list in data.items() if 'on' in v_list]
        kn_packet_id = data['kn_packet'][0]
        kn_packet = KnowledgePacket.objects.get(id=kn_packet_id)
        kn_packet.acquired_by.add(*informed_ids)
        
        send_emails(request, informed_ids, kn_packet=kn_packet)
        messages.info(request, f'Poinformowano wybrane postaci!')
    
    context = {
        'page_title': page_title,
        'skills': skills,
    }
    return render(request, 'knowledge/skills_with_kn_packets.html', context)

#
# @login_required
# def almanac_view(request):
#     profile = request.user.profile
#     skills = prepare_skills(profile)
#
#     # INFORM FORM
#     # dict(request.POST).items() == < QueryDict: {
#     #     'csrfmiddlewaretoken': ['KcoYDwb7r86Ll2SdQUNrDCKs...'],
#     #     '2': ['on'],
#     #     'kn_packet': ['38']
#     # } >
#     if request.method == 'POST' and 'kn_packet' in request.POST:
#         data = dict(request.POST)
#         informed_ids = [k for k, v_list in data.items() if 'on' in v_list]
#         kn_packet_id = data['kn_packet'][0]
#         kn_packet = KnowledgePacket.objects.get(id=kn_packet_id)
#         kn_packet.acquired_by.add(*informed_ids)
#
#         send_emails(request, informed_ids, kn_packet=kn_packet)
#         messages.info(request, f'Poinformowano wybrane postaci!')
#
#     context = {
#         'page_title': 'Almanach',
#         'skills': skills,
#     }
#     return render(request, 'knowledge/skills_with_kn_packets.html', context)
#
#
# @login_required
# def books_view(request):
#     profile = request.user.profile
#     skills = prepare_skills(profile, skill_model=BooksSkill.__name__)
#
#     # INFORM FORM
#     # dict(request.POST).items() == < QueryDict: {
#     #     'csrfmiddlewaretoken': ['KcoYDwb7r86Ll2SdQUNrDCKs...'],
#     #     '2': ['on'],
#     #     'kn_packet': ['38']
#     # } >
#     if request.method == 'POST' and 'kn_packet' in request.POST:
#         data = dict(request.POST)
#         informed_ids = [k for k, v_list in data.items() if 'on' in v_list]
#         kn_packet_id = data['kn_packet'][0]
#         kn_packet = KnowledgePacket.objects.get(id=kn_packet_id)
#         kn_packet.acquired_by.add(*informed_ids)
#
#         send_emails(request, informed_ids, kn_packet=kn_packet)
#         messages.info(request, f'Poinformowano wybrane postaci!')
#
#     context = {
#         'page_title': 'Księgi',
#         'skills': skills,
#     }
#     return render(request, 'knowledge/skills_with_kn_packets.html', context)
#
#
#
# @login_required
# def theology_view(request):
#     profile = request.user.profile
#     skills = prepare_skills(profile, skill_model=TheologySkill)
#
#     # Custom sorting to bring 'Teolog*' skills to the top:
#     # Source: https://stackoverflow.com/questions/11622501/order-query-results-by-startswith-match
#     # Encapsulate the comparison expression.
#     expression = Q(name__startswith='Teolog')
#     # Wrap the expression to specify the field type.
#     is_match = ExpressionWrapper(expression, output_field=BooleanField())
#     # Annotate each object with the comparison.
#     # Order by annotation in reverse; `True` is first (0 < 1); then by name
#     skills = skills.annotate(my_field=is_match)
#     skills = skills.order_by('-my_field', 'name')
#
#     # INFORM FORM
#     # dict(request.POST).items() == < QueryDict: {
#     #     'csrfmiddlewaretoken': ['KcoYDwb7r86Ll2SdQUNrDCKs...'],
#     #     '2': ['on'],
#     #     'kn_packet': ['38']
#     # } >
#     if request.method == 'POST' and 'kn_packet' in request.POST:
#         data = dict(request.POST)
#         informed_ids = [k for k, v_list in data.items() if 'on' in v_list]
#         kn_packet_id = data['kn_packet'][0]
#         kn_packet = KnowledgePacket.objects.get(id=kn_packet_id)
#         kn_packet.acquired_by.add(*informed_ids)
#
#         send_emails(request, informed_ids, kn_packet=kn_packet)
#         messages.info(request, f'Poinformowano wybrane postaci!')
#
#     context = {
#         'page_title': 'Teologia',
#         'skills': skills
#     }
#     return render(request, 'knowledge/skills_with_kn_packets.html', context)
#
#
