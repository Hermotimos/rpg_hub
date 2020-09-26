from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.shortcuts import render, redirect

from rules.models import Profession, Klass
from users.models import Profile


@login_required
def profile_sheet_view(request, profile_id='0'):
    try:
        profile = Profile.objects.get(id=profile_id)
    except Profile.DoesNotExist:
        profile = request.user.profile
        
        
    # Bio
    try:
        birth_event = profile.events_known_directly.first()
        birthplace = birth_event.locations.first()
        birthtime = f'{birth_event.date_start} {birth_event.in_timeunit.name_genetive}'
    except:
        birthplace = 'To skomplikowane...'
        birthtime = 'To skomplikowane...'

    profile_klasses = profile.profile_klasses.select_related('klass__profession')
    profile_klasses = profile_klasses.prefetch_related('levels__achievements')
    
    klasses = Klass.objects.filter(id__in=[pk.klass.id for pk in profile_klasses])
    
    professions = Profession.objects.prefetch_related(
        Prefetch('klasses', queryset=klasses)
    )
    professions = professions.filter(klasses__in=klasses)
    professions = professions.distinct()
    
    context = {
        'page_title': f'Karta postaci',
        'profile': profile,
        'birthplace': birthplace,
        'birthtime': birthtime,
        'professions': professions,
        'profile_klasses': profile_klasses,
    }
    if request.user.profile.status != 'gm' and profile_id != 0:
        return redirect('home:dupa')
    else:
        return render(request, 'development/profile_sheet.html', context)
