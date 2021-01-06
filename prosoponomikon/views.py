from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch, Case, When, Value, IntegerField
from django.shortcuts import render, redirect

from prosoponomikon.forms import GMPersonaGroupCreateForm, \
    PersonaGroupCreateForm
from prosoponomikon.models import PlayerPersona, NPCPersona, \
    PersonaGroup, Persona
from users.models import Profile


@login_required
def prosoponomikon_main_view(request):
    profile = request.user.profile
    if profile.persona_groups_authored.all():
        return redirect('prosoponomikon:personas-grouped')
    else:
        return redirect('prosoponomikon:personas-ungrouped')


@login_required
def prosoponomikon_personas_ungrouped_view(request):
    profile = request.user.profile
    if profile.status == 'gm':
        players = PlayerPersona.objects.prefetch_related('biography_packets')
        npcs = NPCPersona.objects.prefetch_related('biography_packets')
    else:
        known_dir = profile.personas_known_directly.all()
        known_indir = profile.personas_known_indirectly.all()
        known_only_indir = known_indir.exclude(id__in=known_dir)
        
        all_known = (known_dir | known_indir).distinct()
        all_known = all_known.annotate(
            only_indirectly=Case(
                When(id__in=known_only_indir, then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            ),
        )
        all_known = all_known.prefetch_related(
            Prefetch('biography_packets', queryset=profile.authored_bio_packets.all())
        )
        players = all_known.filter(profile=Profile.players.all())
        players = players.exclude(id=profile.persona.id)
        npcs = all_known.filter(profile__in=Profile.npcs.all())

    context = {
        'page_title': 'Prosoponomikon',
        'players': players.select_related('profile'),
        'npcs': npcs.select_related('profile'),
    }
    return render(request, 'prosoponomikon/personas_ungrouped.html', context)


@login_required
def prosoponomikon_personas_grouped_view(request):
    profile = request.user.profile
    persona_groups = PersonaGroup.objects.filter(author=profile)
    
    if profile.status == 'gm':
        persona_groups = persona_groups.prefetch_related(
            'personas__biography_packets')
        ungrouped = Persona.objects.exclude(
            persona_groups__in=persona_groups)
        ungrouped = ungrouped.prefetch_related('biography_packets')
    else:
        known_dir = profile.personas_known_directly.all()
        known_indir = profile.personas_known_indirectly.all()
        known_only_indir = known_indir.exclude(id__in=known_dir)
    
        all_known = (known_dir | known_indir).distinct()
        all_known = all_known.annotate(
            only_indirectly=Case(
                When(id__in=known_only_indir, then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            ),
        )
        all_known = all_known.exclude(id=profile.persona.id)
        all_known = all_known.prefetch_related(
            Prefetch('biography_packets', queryset=profile.authored_bio_packets.all())
        )
        
        persona_groups = persona_groups.prefetch_related(
            Prefetch('personas', queryset=all_known),
            'personas__profile',
        )
        ungrouped = all_known.exclude(persona_groups__in=persona_groups)
        
    context = {
        'page_title': 'Prosoponomikon',
        'persona_groups': persona_groups,
        'ungrouped': ungrouped.prefetch_related('profile'),
    }
    if persona_groups:
        return render(request, 'prosoponomikon/personas_grouped.html', context)
    else:
        return redirect('prosoponomikon:personas-ungrouped')


@login_required
def prosoponomikon_personas_view(request):
    profile = request.user.profile
    if profile.status == 'gm':
        player_personas = PlayerPersona.objects.all()
        npc_personas = NPCPersona.objects.all()
    else:
        player_personas = []
        npc_personas = []
    
    context = {
        'page_title': 'Prosoponomikon',
        'player_personas': player_personas.select_related('profile'),
        'npc_personas': npc_personas.select_related('profile'),
    }
    return render(request, 'prosoponomikon/personas.html', context)


@login_required
def prosoponomikon_persona_group_create_view(request):
    profile = request.user.profile
    if profile.status == 'gm':
        form = GMPersonaGroupCreateForm(data=request.POST or None)
    else:
        form = PersonaGroupCreateForm(data=request.POST or None)
    
    if form.is_valid():
        persona_group = form.save(commit=False)
        persona_group.author = profile
        persona_group.save()
        persona_group.personas.set(form.cleaned_data['personas'])
        messages.success(request, f"Utworzono grupę '{persona_group.name}'!")
        return redirect('prosoponomikon:personas-grouped')
    else:
        messages.warning(request, form.errors)
    
    context = {
        'page_title': 'Nowa grupa',
        'form': form,
    }
    return render(request, '_form.html', context)
