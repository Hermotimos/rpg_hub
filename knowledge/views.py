from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.shortcuts import render, redirect
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie

from imaginarion.models import Picture, PictureImage, PictureSet
from knowledge.forms import KnPacketForm, PlayerKnPacketForm
from knowledge.models import KnowledgePacket
from knowledge.utils import annotate_informables
from rpg_project.utils import handle_inform_form, auth_profile
from rules.models import Skill


@cache_page(60 * 60)
@vary_on_cookie
@login_required
@auth_profile(['all'])
def almanac_view(request):
    current_profile = request.current_profile
    
    knowledge_packets = KnowledgePacket.objects.select_related('author')
    knowledge_packets = annotate_informables(knowledge_packets, current_profile)
    if not current_profile.can_view_all:
        knowledge_packets = knowledge_packets.filter(acquired_by=current_profile)
        
    skills = Skill.objects.filter(knowledge_packets__in=knowledge_packets)
    skills = skills.prefetch_related(
        Prefetch('knowledge_packets', queryset=knowledge_packets),
        'knowledge_packets__picture_sets__pictures',
        'knowledge_packets__references')
    
    if request.method == 'POST':
        handle_inform_form(request)

    context = {
        'page_title': 'Almanach',
        'skills': skills.distinct(),
    }
    return render(request, 'knowledge/skills_with_kn_packets.html', context)


@cache_page(60 * 60)
@vary_on_cookie
@login_required
@auth_profile(['all'])
def kn_packet_form_view(request, kn_packet_id):
    current_profile = request.current_profile
    
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
        return redirect('knowledge:almanac')
    else:
        messages.warning(request, form.errors)
        
    context = {
        'page_title': kn_packet.title if kn_packet else 'Nowy pakiet wiedzy',
        'form': form,
    }
    if not kn_packet_id or current_profile.status == 'gm' \
            or current_profile.knowledge_packets.filter(id=kn_packet_id):
        return render(request, '_form.html', context)
    else:
        return redirect('users:dupa')
