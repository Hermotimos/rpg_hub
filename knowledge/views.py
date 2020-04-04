from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch, Q, ExpressionWrapper, BooleanField
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views import View

from knowledge.models import KnowledgePacket
from rpg_project.utils import query_debugger, send_emails
from rules.models import SkillLevel, Skill


class AlmanacView(View):
    template_name = 'knowledge/skills_with_kn_packets.html'

    @method_decorator(login_required)
    def get(self, request):
        profile = request.user.profile

        if profile.status == 'gm':
            known_kn_packets = KnowledgePacket.objects.all()
        else:
            known_kn_packets = profile.knowledge_packets.all()

        skills = Skill.objects \
            .exclude(name__icontains='Doktryn') \
            .exclude(name__icontains='Teolog') \
            .exclude(name__icontains='Kult') \
            .filter(knowledge_packets__in=known_kn_packets) \
            .prefetch_related(
                Prefetch(
                    'knowledge_packets',
                    queryset=known_kn_packets
                ),
                Prefetch(
                    'skill_levels',
                    queryset=SkillLevel.objects.filter(acquired_by=profile)
                ),
                'knowledge_packets__pictures'
            ).distinct()

        context = {
            'page_title': 'Almanach',
            'skills': skills,
        }
        return render(request, self.template_name, context)

    @method_decorator(login_required)
    def post(self, request):
        # INFORM FORM
        # dict(request.POST).items() == < QueryDict: {
        #     'csrfmiddlewaretoken': ['KcoYDwb7r86Ll2SdQUNrDCKs...'],
        #     '2': ['on'],
        #     'kn_packet': ['38']
        # } >
        if request.method == 'POST' and 'kn_packet' in request.POST:
            data = dict(request.POST)
            informed_ids = [k for k, v_list in data.items() if 'on' in v_list]
            kn_packet_id = data['kn_packet'][0]
            kn_packet = KnowledgePacket.objects.get(id=kn_packet_id)
            kn_packet.acquired_by.add(*informed_ids)

            send_emails(request, informed_ids, kn_packet=kn_packet)
            messages.info(request, f'Poinformowano wybrane postacie!')

        return redirect('knowledge:almanac')


class TheologyView(View):
    template_name = 'knowledge/skills_with_kn_packets.html'

    @method_decorator(login_required)
    def get(self, request):
        profile = request.user.profile

        if profile.status == 'gm':
            theology_skills = Skill.objects.filter(
                Q(name__icontains='Doktryn')
                | Q(name__icontains='Kult')
                | Q(name__icontains='Teologi')
            ).prefetch_related('knowledge_packets__pictures')
        else:
            theology_skills = Skill.objects.filter(
                Q(name__icontains='Doktryn')
                | Q(name__icontains='Kult')
                | Q(name__icontains='Teologi'),
                skill_levels__acquired_by=profile
            ).prefetch_related(
                # Prefetch(
                #     'skill_levels',
                #     queryset=SkillLevel.objects.filter(acquired_by=profile)
                # ),
                Prefetch(
                    'knowledge_packets',
                    queryset=profile.knowledge_packets.all()
                ),
                'knowledge_packets__pictures'
            ).distinct()

        # Custom sorting to bring 'Teolog*' skills to the top:
        # Source: https://stackoverflow.com/questions/11622501/order-query-results-by-startswith-match
        
        search_term = 'Teolog'

        # Encapsulate the comparison expression.
        expression = Q(name__startswith=search_term)

        # Wrap the expression to specify the field type.
        is_match = ExpressionWrapper(expression, output_field=BooleanField())

        # Annotate each object with the comparison.
        theology_skills = theology_skills.annotate(my_field=is_match)

        # Order by the annotated field in reverse, so `True` is first (0 < 1).
        # As second order level user 'name' field
        theology_skills = theology_skills.order_by('-my_field', 'name')

        context = {
            'page_title': 'Teologia',
            'skills': theology_skills
        }
        return render(request, self.template_name, context)
    
    
# class TheologyView(View):
#     template_name = 'knowledge/skills_with_kn_packets.html'
#
#     @method_decorator(login_required)
#     def get(self, request):
#         profile = request.user.profile
#
#         if profile.status == 'gm':
#             theology_skills = Skill.objects.filter(
#                 Q(name__icontains='Doktryn')
#                 | Q(name__icontains='Kult')
#                 | Q(name__icontains='Teologi')
#             ).prefetch_related('skill_levels', 'knowledge_packets__pictures')
#         else:
#             theology_skills = Skill.objects.filter(
#                 Q(name__icontains='Doktryn')
#                 | Q(name__icontains='Kult')
#                 | Q(name__icontains='Teologi')
#             ).prefetch_related(
#                 Prefetch(
#                     'skill_levels',
#                     queryset=SkillLevel.objects.filter(acquired_by=profile)
#                 ),
#                 Prefetch(
#                     'knowledge_packets',
#                     queryset=profile.knowledge_packets.all()
#                 ),
#                 'knowledge_packets__pictures'
#             )
#
#         context = {
#             'page_title': 'Teologia',
#             'theology_skills': theology_skills
#         }
#         return render(request, self.template_name, context)


# @query_debugger
# @login_required
# def almanac_view(request):
#     profile = request.user.profile
#
#     if profile.status == 'gm':
#         known_kn_packets = KnowledgePacket.objects.all()
#     else:
#         known_kn_packets = profile.knowledge_packets.all()
#
#     skills = Skill.objects \
#         .exclude(name__icontains='Doktryn') \
#         .filter(knowledge_packets__in=known_kn_packets) \
#         .prefetch_related(
#             Prefetch('knowledge_packets',
#                      queryset=known_kn_packets),
#             Prefetch('skill_levels',
#                      queryset=SkillLevel.objects.filter(acquired_by=profile)),
#             'knowledge_packets__pictures',
#         ).distinct()
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
#         messages.info(request, f'Poinformowano wybrane postacie!')
#
#     context = {
#         'page_title': 'Almanach',
#         'skills': skills,
#     }
#     return render(request, 'knowledge/skills_with_kn_packets.html', context)


# @query_debugger
# @login_required
# def theology_view(request):
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
#                 queryset=SkillLevel.objects.filter(acquired_by=profile)),
#                 Prefetch('knowledge_packets', queryset=profile.knowledge_packets.all()),
#                 'knowledge_packets__pictures'
#                 )
#
#     context = {
#         'page_title': 'Teologia',
#         'theology_skills': theology_skills
#     }
#     return render(request, 'knowledge/skills_with_kn_packets.html', context)


