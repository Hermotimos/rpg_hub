from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from contact.models import Demand, DemandAnswer
from contact.forms import DemandForm, DemandModifyForm, DemandAnswerForm


@login_required
def main_view(request):
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
    return render(request, 'contact/main.html', context)


@login_required
def create_demand_view(request):
    if request.method == 'POST':
        form = DemandForm(request.POST or None, request.FILES)
        if form.is_valid():
            demand = form.save(commit=False)
            demand.author = request.user
            demand.save()

            if request.user.profile.character_status != 'gm':
                subject = f"[RPG] Zgłoszenie nr {demand.id}"
                message = f"Zgłoszenie od {demand.author.profile}:\n{demand.text}\n" \
                          f"{request.get_host()}/contact/demands/detail:{demand.id}/\n\n"
                sender = settings.EMAIL_HOST_USER
                if request.user.profile.character_status == 'active_player':
                    receivers = ['lukas.kozicki@gmail.com']
                else:
                    receivers = []
                send_mail(subject, message, sender, receivers)

            messages.info(request, f'Zgłoszenie zostało wysłane!')
            return redirect('contact:main')
    else:
        form = DemandForm()

    context = {
        'page_title': 'Zgłoszenie do MG',
        'form': form,
    }
    return render(request, 'contact/create.html', context)


@login_required
def delete_demand_view(request, demand_id):
    demand = get_object_or_404(Demand, id=demand_id)
    demand.delete()
    messages.info(request, 'Usunięto zgłoszenie!')
    return redirect('contact:main')


@login_required
def modify_demand_view(request, demand_id):
    demand = get_object_or_404(Demand, id=demand_id)

    if request.method == 'POST':
        form = DemandModifyForm(instance=demand, data=request.POST or None, files=request.FILES)
        if form.is_valid():
            form.save()

            subject = f"[RPG] Zgłoszenie nr {demand.id}"
            message = f"Modyfikacja przez {demand.author.profile}:\n{demand.text}\n" \
                      f"{request.get_host()}/contact/demands/detail:{demand.id}/\n\n"
            sender = settings.EMAIL_HOST_USER
            if request.user.profile.character_status == 'active_player':
                receivers = ['lukas.kozicki@gmail.com']
            else:
                receivers = []
            send_mail(subject, message, sender, receivers)

            messages.info(request, 'Zmodyfikowano zgłoszenie!')
            return redirect('contact:main')
    else:
        form = DemandModifyForm(instance=demand)

    context = {
        'page_title': 'Modyfikacja zgłoszenia',
        'demand': demand,
        'form': form
    }
    return render(request, 'contact/modify.html', context)


@login_required
def demand_detail_view(request, demand_id):
    demand = get_object_or_404(Demand, id=demand_id)
    answers = DemandAnswer.objects.filter(demand=demand)

    if request.method == 'POST':
        form = DemandAnswerForm(request.POST or None, request.FILES)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.demand = demand
            answer.author = request.user
            answer.save()

            subject = f"[RPG] Zgłoszenie nr {demand.id}"
            message = f"Odpowiedź od {answer.author.profile}:\n{demand.text}\n" \
                      f"{request.get_host()}/contact/demands/detail:{demand.id}/\n\n"
            sender = settings.EMAIL_HOST_USER
            if request.user.profile.character_status == 'active_player':
                receivers = ['lukas.kozicki@gmail.com']
            else:
                receivers = [demand.author.email]
            send_mail(subject, message, sender, receivers)

            messages.info(request, f'Dodano odpowiedź!')
            return redirect('contact:detail', demand_id=demand.id)
    else:
        form = DemandAnswerForm()

    context = {
        'page_title': 'Zgłoszenie - szczegóły',
        'demand': demand,
        'answers': answers,
        'form': form
    }
    return render(request, 'contact/detail.html', context)


@login_required
def mark_done_view(request, demand_id):
    demand = Demand.objects.get(id=demand_id)
    demand.is_done = True
    demand.date_done = timezone.now()
    demand.save()
    DemandAnswer.objects.create(demand=demand, author=request.user, text='Zrobione!')

    subject = f"[RPG] Zgłoszenie nr {demand.id}"
    message = f"{request.user.profile} oznaczył zgłoszenie jako 'zrobione.'\n" \
              f"Zgłoszenie:\n{demand.text}\n" \
              f"{request.get_host()}/contact/demands/detail:{demand.id}/\n\n"
    sender = settings.EMAIL_HOST_USER
    if request.user.profile.character_status == 'active_player':
        receivers = ['lukas.kozicki@gmail.com']
    else:
        receivers = [demand.author.email]
    send_mail(subject, message, sender, receivers)

    messages.info(request, 'Oznaczono jako zrobione!')
    return redirect('contact:main')


@login_required
def mark_done_and_answer_view(request, demand_id):
    demand = get_object_or_404(Demand, id=demand_id)

    if request.method == 'POST':
        form = DemandAnswerForm(request.POST or None, request.FILES)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.demand = demand
            answer.author = request.user
            answer.save()

            demand.is_done = True
            demand.date_done = timezone.now()
            demand.save()

            subject = f"[RPG] Zgłoszenie nr {demand.id}"
            message = f"Zgłoszenie 'zrobione' + odpowiedź:\n{answer.text}\n" \
                      f"{request.get_host()}/contact/demands/detail:{demand.id}/\n\n"
            sender = settings.EMAIL_HOST_USER
            receivers = [demand.author.email]
            send_mail(subject, message, sender, receivers)

            messages.info(request, 'Oznaczono jako zrobione i wysłano odpowiedź!')
            return redirect('contact:main')
    else:
        form = DemandAnswerForm()

    context = {
        'page_title': 'Odpowiedź na zgłoszenie',
        'demand': demand,
        'form': form
    }
    return render(request, 'contact/answer.html', context)


@login_required
def mark_undone_view(request, demand_id):
    demand = get_object_or_404(Demand, id=demand_id)
    demand.is_done = False
    demand.save()

    subject = f"[RPG] Zgłoszenie nr {demand.id}"
    message = f"{request.user.profile} wycofał zgłoszenie jako 'NIE-zrobione'\n" \
              f"Zgłoszenie:\n{demand.text}\n" \
              f"{request.get_host()}/contact/demands/detail:{demand.id}/\n\n"
    sender = settings.EMAIL_HOST_USER
    if request.user.profile.character_status == 'active_player':
        receivers = ['lukas.kozicki@gmail.com']
    else:
        receivers = [demand.author.email]
    send_mail(subject, message, sender, receivers)

    messages.info(request, 'Oznaczono jako niezrobione!')
    return redirect('contact:main')
