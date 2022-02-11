# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render, redirect
#
# from users.models import Profile
#
#
# @login_required
# def character_skills_for_gm_view(request):
#     current_profile = Profile.objects.get(id=request.session['profile_id'])
#     profiles = Profile.players.all()
#
#     context = {
#         'current_profile': current_profile,
#         'page_title': 'Umiejętności graczy',
#         'profiles': profiles,
#     }
#     if current_profile.status == 'gm':
#         return render(
#             request, 'development/character_all_skills_for_gm.html', context)
#     else:
#         return redirect('home:dupa')
#
#
# @login_required
# def character_tricks_view(request):
#     current_profile = Profile.objects.get(id=request.session['profile_id'])
#
#     if current_profile.status == 'gm':
#         players_profiles = Profile.players.filter(is_alive=True)
#     else:
#         players_profiles = [current_profile]
#
#     context = {
#         'current_profile': current_profile,
#         'page_title': f'Podstępy - {current_profile.character}',
#         'players_profiles': players_profiles
#     }
#     return render(request, 'development/character_tricks.html', context)
#
