from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db.models import Prefetch
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404

from knowledge.forms import KnowledgePacketInformForm
from knowledge.models import KnowledgePacket, KnowledgePacketType
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
            .prefetch_related('skill_levels__knowledge_packets')

    else:
        known_kn_packets = KnowledgePacket.objects.filter(allowed_profiles=profile).prefetch_related('pictures')
        kn_packet_types = KnowledgePacketType.objects\
            .prefetch_related(Prefetch('knowledge_packets', queryset=known_kn_packets))
        theology_skills = Skill.objects\
            .filter(skill_levels__acquired_by_characters=profile.character)\
            .filter(name__icontains='Doktryn')\
            .prefetch_related(Prefetch(
                'skill_levels',
                queryset=SkillLevel.objects.filter(acquired_by_characters=profile.character)
                .prefetch_related(Prefetch(
                    'knowledge_packets',
                    queryset=KnowledgePacket.objects.filter(allowed_profiles=profile)
                    ))
            ))\
            .distinct()

    context = {
        'page_title': 'Almanach',
        'kn_packet_types': kn_packet_types,
        'theology_skills': theology_skills
    }
    return render(request, 'knowledge/knowledge_sheet.html', context)


@query_debugger
@login_required
def knowledge_inform_view(request, kn_packet_id):
    profile = request.user.profile
    kn_packet = get_object_or_404(KnowledgePacket, id=kn_packet_id)

    allowed_profiles_old = kn_packet.allowed_profiles.all()

    if request.method == 'POST':
        form = KnowledgePacketInformForm(authenticated_user=request.user,
                                         already_allowed_profiles=allowed_profiles_old,
                                         data=request.POST,
                                         instance=kn_packet)
        if form.is_valid():
            allowed_profiles_new = form.cleaned_data['allowed_profiles']
            kn_packet.allowed_profiles.add(*list(allowed_profiles_new))

            subject = f"[RPG] Transfer wiedzy: '{kn_packet.title}'"
            message = f"{profile} przekazał Ci wiedzę na temat: '{kn_packet.title}'.\n"\
                f"Więdzę tę możesz odnaleźć w zakładce Wiedza/Okruchy wiedzy: " \
                f"{request.get_host()}/knowledge/knowledge-sheet/\n"\
                f"Zobaczysz tam, z jakimi elementami jest powiązana ta wiedza (Umiejętności, Toponomikon itp.).\n" \
                f"Wiedzę możesz przeglądać zarówno w Okruchach wiedzy, jak i we wskazanych tam miejscach."
            sender = settings.EMAIL_HOST_USER
            receivers = []
            for p in allowed_profiles_new:
                receivers.append(p.user.email)
            if profile.character_status != 'gm':
                receivers.append('lukas.kozicki@gmail.com')
            send_mail(subject, message, sender, receivers)

            messages.info(request, f'Podzieliłeś się wiedzą z wybranymi towarzyszami!')
            _next = request.POST.get('next', '/')
            return HttpResponseRedirect(_next)
    else:
        form = KnowledgePacketInformForm(authenticated_user=request.user,
                                         already_allowed_profiles=allowed_profiles_old)

    context = {
        'page_title': 'Podziel się wiedzą',
        'kn_packet': kn_packet,
        'form': form,
    }
    if profile in kn_packet.allowed_profiles.all() or profile.character_status == 'gm':
        return render(request, 'knowledge/knowledge_inform.html', context)
    else:
        return redirect('home:dupa')
