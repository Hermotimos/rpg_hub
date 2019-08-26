from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from django.http import HttpResponseRedirect
from users.models import User
from contact.models import Demand, DemandAnswer
from contact.forms import DemandsCreateForm, PlansCreateForm, DemandsModifyForm, DemandAnswerForm


# ----------------------------- DEMANDS -----------------------------


@login_required
def demands_main_view(request):
    received_demands_undone = \
        Demand.objects.filter(is_done=False, addressee=request.user).exclude(author=request.user)
    received_demands_done = \
        Demand.objects.filter(is_done=True, addressee=request.user).exclude(author=request.user)
    sent_demands_undone = \
        Demand.objects.filter(is_done=False, author=request.user).exclude(addressee=request.user)
    sent_demands_done = \
        Demand.objects.filter(is_done=True, author=request.user).exclude(addressee=request.user)

    context = {
        'page_title': 'Dezyderaty',
        'received_demands_undone': received_demands_undone,
        'received_demands_done': received_demands_done,
        'sent_demands_undone': sent_demands_undone,
        'sent_demands_done': sent_demands_done
    }
    return render(request, 'contact/demands-main.html', context)


@login_required
def demands_create_view(request):
    if request.method == 'POST':
        form = DemandsCreateForm(request.POST or None, request.FILES)
        if form.is_valid():
            demand = form.save(commit=False)
            demand.author = request.user
            demand.save()

            if request.user.profile.character_status != 'gm':
                subject = f"[RPG] Dezyderat nr {demand.id}"
                message = f"Dezyderat od {demand.author}:\n{demand.text}\n" \
                          f"{request.get_host()}/contact/demands/detail:{demand.id}/\n\n"
                sender = settings.EMAIL_HOST_USER
                if request.user.profile.character_status == 'active_player':
                    receivers = ['lukas.kozicki@gmail.com']
                else:
                    receivers = []
                send_mail(subject, message, sender, receivers)

            messages.info(request, f'Dezyderat został wysłany!')
            _next = request.POST.get('next', '/')
            return HttpResponseRedirect(_next)
    else:
        form = DemandsCreateForm(initial={'addressee': User.objects.get(username='MG')})

    context = {
        'page_title': 'Nowy dezyderat',
        'form': form,
    }
    return render(request, 'contact/demands-create.html', context)


@login_required
def demands_delete_view(request, demand_id):
    demand = get_object_or_404(Demand, id=demand_id)
    if request.user == demand.author:
        demand.delete()
        messages.info(request, 'Usunięto dezyderat!')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        return redirect('home:dupa')


@login_required
def demands_modify_view(request, demand_id):
    demand = get_object_or_404(Demand, id=demand_id)

    if request.method == 'POST':
        form = DemandsModifyForm(instance=demand, data=request.POST or None, files=request.FILES)
        if form.is_valid():
            form.save()

            subject = f"[RPG] Dezyderat nr {demand.id}"
            message = f"Modyfikacja przez {demand.author}:\n{demand.text}\n" \
                      f"{request.get_host()}/contact/demands/detail:{demand.id}/\n\n"
            sender = settings.EMAIL_HOST_USER
            if request.user.profile.character_status == 'active_player':
                receivers = ['lukas.kozicki@gmail.com']
            else:
                receivers = []
            send_mail(subject, message, sender, receivers)

            messages.info(request, 'Zmodyfikowano dezyderat!')
            _next = request.POST.get('next', '/')
            return HttpResponseRedirect(_next)
    else:
        form = DemandsModifyForm(instance=demand)

    context = {
        'page_title': 'Modyfikacja dezyderatu',
        'demand': demand,
        'form': form
    }
    if request.user == demand.author:
        return render(request, 'contact/demands-modify.html', context)
    else:
        return redirect('home:dupa')


@login_required
def demands_detail_view(request, demand_id):
    demand = get_object_or_404(Demand, id=demand_id)
    answers = DemandAnswer.objects.filter(demand=demand)

    if request.method == 'POST':
        form = DemandAnswerForm(request.POST or None, request.FILES)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.demand = demand
            answer.author = request.user
            answer.save()

            subject = f"[RPG] Dezyderat nr {demand.id}"
            message = f"Odpowiedź od {answer.author}:\n{answer.text}\n" \
                      f"{request.get_host()}/contact/demands/detail:{demand.id}/\n\n"
            sender = settings.EMAIL_HOST_USER
            if request.user.profile.character_status == 'active_player':
                receivers = ['lukas.kozicki@gmail.com']
            else:
                receivers = [demand.author.email]
            send_mail(subject, message, sender, receivers)

            messages.info(request, f'Dodano odpowiedź!')
            _next = request.POST.get('next', '/')
            return HttpResponseRedirect(_next)
    else:
        form = DemandAnswerForm()

    context = {
        'page_title': 'Dezyderat - szczegóły',
        'demand': demand,
        'answers': answers,
        'form': form
    }
    if request.user in [demand.author, demand.addressee]:
        return render(request, 'contact/demands-detail.html', context)
    else:
        return redirect('home:dupa')


# ----------------------------- PLANS -----------------------------


@login_required
def plans_main_view(request):
    self_demands_undone = \
        Demand.objects.filter(is_done=False, addressee=request.user, author=request.user)
    self_demands_done = \
        Demand.objects.filter(is_done=True, addressee=request.user, author=request.user)

    context = {
        'page_title': 'Plany',
        'self_demands_undone': self_demands_undone,
        'self_demands_done': self_demands_done,
    }
    return render(request, 'contact/plans-main.html', context)


@login_required
def plans_create_view(request):
    if request.method == 'POST':
        form = PlansCreateForm(request.POST or None, request.FILES)
        if form.is_valid():
            demand = form.save(commit=False)
            demand.author = request.user
            demand.addressee = request.user
            demand.save()
            messages.info(request, f'Plan został zapisany!')
            _next = request.POST.get('next', '/')
            return HttpResponseRedirect(_next)
    else:
        form = PlansCreateForm(initial={'addressee': request.user.profile})

    context = {
        'page_title': 'Nowy plan',
        'form': form,
    }
    return render(request, 'contact/plans-create.html', context)


@login_required
def plans_delete_view(request, demand_id):
    demand = get_object_or_404(Demand, id=demand_id)
    if request.user == demand.author:
        demand.delete()
        messages.info(request, 'Usunięto plan!')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        return redirect('home:dupa')


@login_required
def plans_modify_view(request, demand_id):
    demand = get_object_or_404(Demand, id=demand_id)
    if request.method == 'POST':
        form = DemandsModifyForm(instance=demand, data=request.POST or None, files=request.FILES)
        if form.is_valid():
            form.save()
            messages.info(request, 'Zmodyfikowano plan!')
            _next = request.POST.get('next', '/')
            return HttpResponseRedirect(_next)
    else:
        form = DemandsModifyForm(instance=demand)

    context = {
        'page_title': 'Zmiana planów?',
        'demand': demand,
        'form': form
    }
    if request.user == demand.author:
        return render(request, 'contact/plans-modify.html', context)
    else:
        return redirect('home:dupa')


# ----------------------------- DEMANDS & PLANS -----------------------------


@login_required
def mark_done_view(request, demand_id):
    demand = Demand.objects.get(id=demand_id)
    if request.user in [demand.author, demand.addressee]:
        demand.is_done = True
        demand.date_done = timezone.now()
        demand.save()
        DemandAnswer.objects.create(demand=demand, author=request.user, text='Zrobione!')

        subject = f"[RPG] Dezyderat nr {demand.id}"
        message = f"{request.user.profile} oznaczył dezyderat jako 'zrobiony'.\n" \
                  f"Dezyderat:\n{demand.text}\n" \
                  f"{request.get_host()}/contact/demands/detail:{demand.id}/\n\n"
        sender = settings.EMAIL_HOST_USER
        if request.user.profile.character_status == 'active_player':
            receivers = ['lukas.kozicki@gmail.com']
        else:
            receivers = [demand.author.email]
        send_mail(subject, message, sender, receivers)

        messages.info(request, 'Oznaczono jako zrobiony!')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    else:
        return redirect('home:dupa')


@login_required
def mark_undone_view(request, demand_id):
    demand = get_object_or_404(Demand, id=demand_id)
    if request.user in [demand.author, demand.addressee]:
        demand.is_done = False
        demand.save()

        subject = f"[RPG] Dezyderat nr {demand.id}"
        message = f"{request.user.profile} cofnął dezyderat jako 'NIE-zrobiony'.\n" \
                  f"Dezyderat:\n{demand.text}\n" \
                  f"{request.get_host()}/contact/demands/detail:{demand.id}/\n\n"
        sender = settings.EMAIL_HOST_USER
        if request.user.profile.character_status == 'active_player':
            receivers = ['lukas.kozicki@gmail.com']
        else:
            receivers = [demand.author.email]
        send_mail(subject, message, sender, receivers)

        messages.info(request, 'Oznaczono jako niezrobiony!')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    else:
        return redirect('home:dupa')
