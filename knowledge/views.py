from datetime import datetime

from django.apps import apps
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch, Q, ExpressionWrapper, BooleanField
from django.shortcuts import render, redirect

from imaginarion.models import Picture, PictureImage, PictureSet
from knowledge.forms import KnPacketForm, PlayerKnPacketForm
from knowledge.models import KnowledgePacket
from rpg_project.utils import handle_inform_form
from rules.models import Skill
from users.models import Profile


@login_required
def almanac_view(request):
    current_profile = Profile.objects.get(id=request.session['profile_id'])
    
    kn_packets = KnowledgePacket.objects.all()
    if not current_profile.can_view_all:
        kn_packets = kn_packets.filter(acquired_by=current_profile)
    
    skills = Skill.objects.filter(knowledge_packets__in=kn_packets)
    skills = skills.prefetch_related(
        Prefetch('knowledge_packets', queryset=kn_packets),
        'knowledge_packets__picture_sets__pictures')
    
    if request.method == 'POST':
        handle_inform_form(request)

    context = {
        'current_profile': current_profile,
        'page_title': 'Almanach',
        'skills': skills.distinct(),
    }
    return render(request, 'knowledge/skills_with_kn_packets.html', context)


@login_required
def kn_packet_form_view(request, kn_packet_id):
    current_profile = Profile.objects.get(id=request.session['profile_id'])
    kn_packet = KnowledgePacket.objects.filter(id=kn_packet_id).first()
        
    if current_profile.status == 'gm':
        form = KnPacketForm(data=request.POST or None,
                            files=request.FILES or None,
                            instance=kn_packet)
    else:
        form = PlayerKnPacketForm(data=request.POST or None,
                                  files=request.FILES or None,
                                  instance=kn_packet,
                                  current_profile=current_profile)
    
    if form.is_valid():
        if current_profile.status == 'gm':
            kn_packet = form.save()
        else:
            kn_packet = form.save(commit=False)
            kn_packet.author = current_profile
            kn_packet.save()
            kn_packet.acquired_by.add(current_profile)
            kn_packet.skills.set(form.cleaned_data['skills'])

            pictures = [v for k, v in form.cleaned_data.items()
                        if 'picture' in k and v is not None]
            
            new_pictures = []
            for cnt, picture in enumerate(pictures, 1):
                description = (form.cleaned_data[f'descr_{cnt}']
                               or f"{kn_packet.title}")
                pic_img = PictureImage.objects.create(
                    image=picture,
                    description=description)
                pic = Picture.objects.create(
                    image=pic_img,
                    type='players-notes',
                    description=description)
                new_pictures.append(pic)
            
            if new_pictures:
                now = datetime.now().strftime("%Y-%d-%m %H:%M:%S")
                title = f"""
                    KnowledgePacket: '{kn_packet.title}'
                    [Autor: {current_profile.character.first_name} - {now}]
                """
                new_picture_set = PictureSet.objects.create(title=title)
                new_picture_set.pictures.set(new_pictures)
                kn_packet.picture_sets.add(new_picture_set)
            
        for location in form.cleaned_data['locations']:
            location.knowledge_packets.add(kn_packet)
            
        messages.success(
            request, f'Zapisano pakiet wiedzy "{kn_packet.title}"!')
        return redirect('knowledge:almanac', 'Skill')
    else:
        messages.warning(request, form.errors)
        
    context = {
        'current_profile': current_profile,
        'page_title': kn_packet.title if kn_packet else 'Nowy pakiet wiedzy',
        'form': form,
    }
    if not kn_packet_id or current_profile.status == 'gm' \
            or current_profile.knowledge_packets.filter(id=kn_packet_id):
        return render(request, '_form.html', context)
    else:
        return redirect('users:dupa')
