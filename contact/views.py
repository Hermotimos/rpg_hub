from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.mail import send_mail
from contact.models import Demand, DemandAnswer
from contact.forms import DemandForm, DemandAnswerForm


@login_required
def demand_view(request):
    if request.method == 'POST':
        form = DemandForm(request.POST or None)
        if form.is_valid():
            demand = form.save(commit=False)
            demand.author = request.user
            demand.save()

            if request.user.profile.character_status != 'gm':
                subject = f"[RPG] Zgłoszenie od {request.user.profile}"
                message = f"{request.user.profile} zgłasza:\n" \
                          f"{form.cleaned_data['text']}"
                sender = settings.EMAIL_HOST_USER
                receivers_list = ['lukas.kozicki@gmail.com']
                send_mail(subject, message, sender, receivers_list)

            messages.info(request, f'Zgłoszenie zostało wysłane!')
            return redirect('contact:demands-list')
    else:
        form = DemandForm()

    context = {
        'page_title': 'Zgłoszenie do MG',
        'form': form,
    }
    return render(request, 'contact/demand.html', context)


@login_required
def demands_list_view(request):
    if request.user.profile.character_status == 'gm':
        demands_undone = Demand.objects.filter(is_done=False)
        demands_done = Demand.objects.filter(is_done=True)
    else:
        demands_undone = Demand.objects.filter(is_done=False, author=request.user)
        demands_done = Demand.objects.filter(is_done=True, author=request.user)

    context = {
        'page_title': 'Zgłoszenia',
        'demands_undone': demands_undone,
        'demands_done': demands_done
    }
    return render(request, 'contact/demands_list.html', context)


@login_required
def mark_done_view(request, demand_id):
    obj = Demand.objects.get(id=demand_id)
    obj.is_done = True
    obj.response = 'Zrobione!'
    obj.save()
    messages.info(request, 'Oznaczono jako zrobione!')
    return redirect('contact:demands-list')


@login_required
def mark_done_and_answer_view(request, demand_id):
    demand = get_object_or_404(Demand, id=demand_id)

    if request.method == 'POST':
        form = DemandAnswerForm(instance=demand, data=request.POST or None)
        if form.is_valid():
            demand.is_done = True
            form.save()
            messages.info(request, 'Oznaczono jako zrobione!')
            return redirect('contact:demands-list')
    else:
        form = DemandAnswerForm(instance=demand)

    context = {
        'page_title': 'Odpowiedź na zgłoszenie',
        'demand': demand,
        'form': form
    }
    return render(request, 'contact/answer.html', context)


@login_required
def mark_undone_view(request, demand_id):
    obj = Demand.objects.get(id=demand_id)
    obj.is_done = False
    obj.save()
    messages.info(request, 'Oznaczono jako niezrobione!')
    return redirect('contact:demands-list')
