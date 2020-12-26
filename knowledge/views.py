from datetime import datetime

from django.apps import apps
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch, Q, ExpressionWrapper, BooleanField
from django.shortcuts import render, redirect

from imaginarion.models import Picture
from knowledge.forms import KnPacketCreateForm, PlayerKnPacketCreateForm
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
    
    page_title = skill_model._meta.verbose_name
    if page_title == 'Księgi':
        page_title = 'Biblioteka'
    elif skill_model == Skill:
        page_title = 'Almanach'
    
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
    if page_title != 'Almanach':
        skills = custom_sort(skills)
    
    if request.method == 'POST':
        handle_inform_form(request)
    
    context = {
        'page_title': page_title,
        'skills': skills,
    }
    return render(request, 'knowledge/skills_with_kn_packets.html', context)


@login_required
def kn_packet_create_and_update_view(request, kn_packet_id):
    profile = request.user.profile
    try:
        kn_packet = KnowledgePacket.objects.get(id=kn_packet_id)
    except KnowledgePacket.DoesNotExist:
        kn_packet = None
        
    if profile.status == 'gm':
        form = KnPacketCreateForm(data=request.POST or None,
                                  files=request.FILES or None,
                                  instance=kn_packet)
    else:
        form = PlayerKnPacketCreateForm(data=request.POST or None,
                                        files=request.FILES or None,
                                        instance=kn_packet,
                                        profile=profile)
    
    if form.is_valid():
        if profile.status == 'gm':
            kn_packet = form.save()
        else:
            kn_packet = form.save(commit=False)
            kn_packet.author = profile
            kn_packet.save()
            
            kn_packet.acquired_by.add(profile)
            kn_packet.skills.set(form.cleaned_data['skills'])

            pictures = [v for k, v in form.cleaned_data.items()
                        if 'picture' in k and v is not None]
            for cnt, picture in enumerate(pictures, 1):
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                pic = Picture.objects.create(
                    image=picture,
                    type='players-notes',
                    title=f'PLAYERS-NOTES__{profile}_{now}_[{cnt}]',
                    description=form.cleaned_data[f'description_{cnt}'] or now,
                )
                kn_packet.pictures.add(pic)
            
        for location in form.cleaned_data['locations']:
            location.knowledge_packets.add(kn_packet)
            
        if not kn_packet_id:
            messages.success(request, f'Utworzono "{kn_packet.title}"!')
        else:
            messages.success(request, f'Zmieniono "{kn_packet.title}"!')
        return redirect('knowledge:knowledge-packets-in-skills', 'Skill')
    else:
        messages.warning(request, form.errors)
        
    context = {
        'page_title': kn_packet.title if kn_packet else 'Nowy pakiet wiedzy',
        'form': form,
    }
    if not kn_packet_id or profile.status == 'gm' \
            or profile.knowledge_packets.filter(id=kn_packet_id):
        return render(request, '_form.html', context)
    else:
        return redirect('home:dupa')
