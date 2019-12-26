from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404

from knowledge.forms import KnowledgePacketInformForm
from knowledge.models import KnowledgePacket
from rpg_project import settings
from rpg_project.utils import query_debugger
from rules.models import SkillLevel
from toponomikon.models import GeneralLocation, SpecificLocation


@query_debugger
@login_required
def knowledge_sheet_view(request):
    profile = request.user.profile
    if profile.character_status == 'gm':
        skills_kn_packets = KnowledgePacket.objects\
            .filter(skill_levels__in=SkillLevel.objects.all())\
            .prefetch_related('pictures')
        toponomikon_kn_packets = (
                KnowledgePacket.objects.filter(general_locations__in=GeneralLocation.objects.all()) |
                KnowledgePacket.objects.filter(specific_locations__in=SpecificLocation.objects.all())
        )\
            .distinct()\
            .prefetch_related('pictures')
    else:
        skills_kn_packets = KnowledgePacket.objects\
            .filter(skill_levels__in=profile.character.skill_levels_acquired.all())\
            .prefetch_related('pictures')

        known_gen_locs = (profile.gen_locs_known_directly.all() | profile.gen_locs_known_indirectly.all()).distinct()
        known_spec_locs = (profile.spec_locs_known_directly.all() | profile.spec_locs_known_indirectly.all()).distinct()
        toponomikon_kn_packets = (
                KnowledgePacket.objects.filter(general_locations__in=known_gen_locs) |
                KnowledgePacket.objects.filter(specific_locations__in=known_spec_locs)
        )\
            .distinct()\
            .prefetch_related('pictures')

    context = {
        'page_title': 'Okruchy wiedzy',
        'skills_kn_packets': skills_kn_packets,
        'toponomikon_kn_packets': toponomikon_kn_packets,
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

            messages.info(request, f'Dokonałeś transferu wiedzy do wybranych postaci!')
            _next = request.POST.get('next', '/')
            return HttpResponseRedirect(_next)
    else:
        form = KnowledgePacketInformForm(authenticated_user=request.user,
                                         already_allowed_profiles=allowed_profiles_old)

    context = {
        'page_title': 'Dokonaj transferu wiedzy',
        'kn_packet': kn_packet,
        'form': form,
    }
    if profile in kn_packet.allowed_profiles.all() or profile.character_status == 'gm':
        return render(request, 'knowledge/knowledge_inform.html', context)
    else:
        return redirect('home:dupa')
