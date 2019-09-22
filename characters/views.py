from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required


@login_required
def tricks_sheet_view(request):
    context = {
        'page_title': f'Podstępy - {request.user.profile.character_name}'
    }
    return render(request, 'characters/tricks_sheet.html', context)
