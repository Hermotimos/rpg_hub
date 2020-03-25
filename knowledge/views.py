from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db.models import Prefetch, Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import ListView

from knowledge.models import KnowledgePacket
from rpg_project import settings
from rpg_project.utils import query_debugger
from rules.models import SkillLevel, Skill


# @query_debugger
# @login_required
# def almanac_view(request):
#     profile = request.user.profile
#
#     if profile.status == 'gm':
#         known_kn_packets = KnowledgePacket.objects.all()
#         skills_with_kn_packets = Skill.objects\
#             .exclude(name__icontains='Doktryn')\
#             .filter(knowledge_packets__in=known_kn_packets)\
#             .prefetch_related(
#                 Prefetch('knowledge_packets', queryset=known_kn_packets),
#                 Prefetch('skill_levels',
#                 queryset=SkillLevel.objects.filter(acquired_by_characters=profile.character)),
#                 'knowledge_packets__pictures'
#             )\
#             .distinct()
#     else:
#         known_kn_packets = profile.character.knowledge_packets.all()
#         skills_with_kn_packets = Skill.objects\
#             .exclude(name__icontains='Doktryn') \
#             .filter(knowledge_packets__in=known_kn_packets)\
#             .prefetch_related(
#                 Prefetch('knowledge_packets', queryset=known_kn_packets),
#                 Prefetch('skill_levels',
#                 queryset=SkillLevel.objects.filter(acquired_by_characters=profile.character)),
#                 'knowledge_packets__pictures'
#             )\
#             .distinct()
#
#     context = {
#         'page_title': 'Almanach',
#         'skills_with_kn_packets': skills_with_kn_packets
#     }
#     return render(request, 'knowledge/almanac.html', context)


class AlmanacView(View):

    @method_decorator(login_required)
    def get(self, request):
        profile = request.user.profile

        if profile.status == 'gm':
            known_kn_packets = KnowledgePacket.objects.all()
            skills_with_kn_packets = Skill.objects \
                .exclude(name__icontains='Doktryn') \
                .filter(knowledge_packets__in=known_kn_packets) \
                .prefetch_related(
                    Prefetch('knowledge_packets', queryset=known_kn_packets),
                    Prefetch('skill_levels',
                             queryset=SkillLevel.objects.filter(acquired_by_characters=profile.character)),
                    'knowledge_packets__pictures'
                ) \
                .distinct()
        else:
            known_kn_packets = profile.character.knowledge_packets.all()
            skills_with_kn_packets = Skill.objects \
                .exclude(name__icontains='Doktryn') \
                .filter(knowledge_packets__in=known_kn_packets) \
                .prefetch_related(
                    Prefetch('knowledge_packets', queryset=known_kn_packets),
                    Prefetch('skill_levels',
                             queryset=SkillLevel.objects.filter(acquired_by_characters=profile.character)),
                    'knowledge_packets__pictures'
                )\
                .distinct()

        context = {
            'page_title': 'Almanach',
            'skills_with_kn_packets': skills_with_kn_packets
        }
        return render(request, 'knowledge/almanac.html', context)


# @query_debugger
# @login_required
# def knowledge_theology_view(request):
#     profile = request.user.profile
#
#     if profile.status == 'gm':
#         theology_skills = Skill.objects\
#             .filter(name__icontains='Doktryn')\
#             .prefetch_related('skill_levels', 'knowledge_packets__pictures')
#     else:
#         theology_skills = Skill.objects\
#             .filter(name__icontains='Doktryn')\
#             .prefetch_related(
#                 Prefetch('skill_levels',
#                 queryset=SkillLevel.objects.filter(acquired_by_characters=profile.character)),
#                 Prefetch('knowledge_packets', queryset=profile.character.knowledge_packets.all()),
#                 'knowledge_packets__pictures'
#                 )
#
#     context = {
#         'page_title': 'Teologia',
#         'theology_skills': theology_skills
#     }
#     return render(request, 'knowledge/knowledge_theology.html', context)


class TheologyView(View):
    template_name = 'knowledge/knowledge_theology.html'

    @method_decorator(login_required)
    def get(self, request):
        profile = request.user.profile

        if profile.status == 'gm':
            theology_skills = Skill.objects \
                .filter(Q(name__icontains='Doktryn') | Q(name__icontains='Kult') | Q(name__icontains='Teologi')) \
                .prefetch_related('skill_levels', 'knowledge_packets__pictures')
        else:
            theology_skills = Skill.objects \
                .filter(Q(name__icontains='Doktryn') | Q(name__icontains='Kult') | Q(name__icontains='Teologi')) \
                .prefetch_related(
                    Prefetch('skill_levels',
                             queryset=SkillLevel.objects.filter(acquired_by_characters=profile.character)),
                    Prefetch('knowledge_packets', queryset=profile.character.knowledge_packets.all()),
                    'knowledge_packets__pictures'
                )

        context = {
            'page_title': 'Teologia',
            'theology_skills': theology_skills
        }
        return render(request, self.template_name, context)
