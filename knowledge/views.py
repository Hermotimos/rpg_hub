from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db.models import Prefetch
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404

from knowledge.forms import KnowledgePacketInformForm
from knowledge.models import KnowledgePacket
from rpg_project import settings
from rpg_project.utils import query_debugger
from rules.models import SkillLevel, Skill


@query_debugger
@login_required
def knowledge_sheet_view(request):
    profile = request.user.profile
    if profile.character_status == 'gm':
        kn_packet_types = KnowledgePacketType.objects.prefetch_related('knowledge_packets__pictures')
        theology_skills = Skill.objects\
            .filter(name__icontains='Doktryn')\
            .prefetch_related('skill_levels__knowledge_packets__pictures')
    else:
        known_kn_packets = KnowledgePacket.objects.filter(allowed_profiles=profile).prefetch_related('pictures')
        kn_packet_types = KnowledgePacketType.objects\
            .prefetch_related(Prefetch('knowledge_packets', queryset=known_kn_packets))\
            # .filter(knowledge_packets__in=known_kn_packets)
        theology_skills = Skill.objects\
            .filter(skill_levels__acquired_by_characters=profile.character)\
            .filter(name__icontains='Doktryn')\
            .prefetch_related(Prefetch(
                'skill_levels',
                queryset=SkillLevel.objects.filter(acquired_by_characters=profile.character)
                .prefetch_related(Prefetch('knowledge_packets', queryset=known_kn_packets))
            ))\
            .distinct()

    context = {
        'page_title': 'Almanach',
        'kn_packet_types': kn_packet_types,
        'theology_skills': theology_skills
    }
    return render(request, 'knowledge/knowledge_almanac.html', context)


@query_debugger
@login_required
def knowledge_theology_view(request):
    profile = request.user.profile

    if profile.character_status == 'gm':
        theology_skills = Skill.objects\
            .filter(name__icontains='Doktryn')\
            .prefetch_related('skill_levels', 'knowledge_packets__pictures')
    else:
        theology_skills = Skill.objects\
            .filter(name__icontains='Doktryn')\
            .prefetch_related(
                Prefetch('skill_levels', queryset=SkillLevel.objects.filter(acquired_by_characters=profile.character)),
                Prefetch('knowledge_packets', queryset=profile.character.knowledge_packets.all()),
                'knowledge_packets__pictures'
                )

    context = {
        'page_title': 'Teologia',
        'theology_skills': theology_skills
    }
    return render(request, 'knowledge/knowledge_theology.html', context)


@query_debugger
@login_required
def knowledge_inform_view(request, kn_packet_id):
    profile = request.user.profile
    kn_packet = get_object_or_404(KnowledgePacket, id=kn_packet_id)

    allowed_characters_old = kn_packet.characters.all()

    if request.method == 'POST':
        form = KnowledgePacketInformForm(authenticated_user=request.user,
                                         allowed_characters_old=allowed_characters_old,
                                         data=request.POST,
                                         instance=kn_packet)
        if form.is_valid():
            characters_new = form.cleaned_data['characters']
            for character in characters_new:
                character.knowledge_packets.add(kn_packet)

            subject = f"[RPG] Transfer wiedzy: '{kn_packet.title}'"
            message = f"{profile} przekazał Ci wiedzę na temat: '{kn_packet.title}'.\n"\
                f"Więdzę tę możesz odnaleźć w zakładce Wiedza/Okruchy wiedzy: " \
                f"{request.get_host()}/knowledge/almanac/\n"\
                f"Zobaczysz tam, z jakimi elementami jest powiązana ta wiedza (Umiejętności, Toponomikon itp.).\n" \
                f"Wiedzę możesz przeglądać zarówno w Okruchach wiedzy, jak i we wskazanych tam miejscach."
            sender = settings.EMAIL_HOST_USER
            receivers = []
            for profile in [ch.profile for ch in characters_new]:
                receivers.append(profile.user.email)
            if profile.character_status != 'gm':
                receivers.append('lukas.kozicki@gmail.com')
            send_mail(subject, message, sender, receivers)

            messages.info(request, f'Podzieliłeś się wiedzą z wybranymi towarzyszami!')
            _next = request.POST.get('next', '/')
            return HttpResponseRedirect(_next)
    else:
        form = KnowledgePacketInformForm(authenticated_user=request.user,
                                         allowed_characters_old=allowed_characters_old)

    context = {
        'page_title': 'Podziel się wiedzą',
        'kn_packet': kn_packet,
        'form': form,
    }
    if kn_packet in profile.character.knowledge_packets.all() or profile.character_status == 'gm':
        return render(request, 'knowledge/knowledge_inform.html', context)
    else:
        return redirect('home:dupa')
