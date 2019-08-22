from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from django.http import HttpResponseRedirect
from contact.models import Demand, DemandAnswer
from contact.forms import DemandForm, DemandTodoForm, DemandModifyForm, DemandAnswerForm


@login_required
def main_view(request):
    received_demands_undone = \
        Demand.objects.filter(is_done=False, addressee=request.user.profile).exclude(author=request.user.profile)
    received_demands_done = \
        Demand.objects.filter(is_done=True, addressee=request.user.profile).exclude(author=request.user.profile)
    sent_demands_undone = \
        Demand.objects.filter(is_done=False, author=request.user.profile).exclude(addressee=request.user.profile)
    sent_demands_done = \
        Demand.objects.filter(is_done=True, author=request.user.profile).exclude(addressee=request.user.profile)

    context = {
        'page_title': 'Dezyderaty',
        'received_demands_undone': received_demands_undone,
        'received_demands_done': received_demands_done,
        'sent_demands_undone': sent_demands_undone,
        'sent_demands_done': sent_demands_done
    }
    return render(request, 'contact/main.html', context)


@login_required
def todo_view(request):
    self_demands_undone = \
        Demand.objects.filter(is_done=False, addressee=request.user.profile, author=request.user.profile)
    self_demands_done = \
        Demand.objects.filter(is_done=True, addressee=request.user.profile, author=request.user.profile)

    context = {
        'page_title': 'Plany',
        'self_demands_undone': self_demands_undone,
        'self_demands_done': self_demands_done,
    }
    return render(request, 'contact/todo.html', context)


@login_required
def create_demand_view(request):
    if request.method == 'POST':
        form = DemandForm(request.POST or None, request.FILES)
        if form.is_valid():
            demand = form.save(commit=False)
            demand.author = request.user.profile
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
            return redirect('contact:main')
    else:
        form = DemandForm()

    context = {
        'page_title': 'Nowy dezyderat',
        'form': form,
    }
    return render(request, 'contact/create.html', context)


@login_required
def create_todo_view(request):
    if request.method == 'POST':
        form = DemandTodoForm(request.POST or None, request.FILES)
        if form.is_valid():
            demand = form.save(commit=False)
            demand.author = request.user.profile
            demand.addressee = request.user.profile
            demand.save()
            messages.info(request, f'Plan został zapisany!')
            return redirect('contact:todo')
    else:
        form = DemandForm(initial={'addressee': request.user.profile})

    context = {
        'page_title': 'Nowy plan',
        'form': form,
    }
    return render(request, 'contact/create-todo.html', context)


@login_required
def delete_demand_view(request, demand_id):
    demand = get_object_or_404(Demand, id=demand_id)
    demand.delete()
    messages.info(request, 'Usunięto!')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def modify_demand_view(request, demand_id):
    demand = get_object_or_404(Demand, id=demand_id)

    if request.method == 'POST':
        form = DemandModifyForm(instance=demand, data=request.POST or None, files=request.FILES)
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
            return redirect('contact:main')
    else:
        form = DemandModifyForm(instance=demand)

    context = {
        'page_title': 'Modyfikacja dezyderatu',
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
            answer.author = request.user.profile
            answer.save()

            subject = f"[RPG] Dezyderat nr {demand.id}"
            message = f"Odpowiedź od {answer.author}:\n{demand.text}\n" \
                      f"{request.get_host()}/contact/demands/detail:{demand.id}/\n\n"
            sender = settings.EMAIL_HOST_USER
            if request.user.profile.character_status == 'active_player':
                receivers = ['lukas.kozicki@gmail.com']
            else:
                receivers = [demand.author.user.email]
            send_mail(subject, message, sender, receivers)

            messages.info(request, f'Dodano odpowiedź!')
            return redirect('contact:detail', demand_id=demand.id)
    else:
        form = DemandAnswerForm()

    context = {
        'page_title': 'Dezyderat - szczegóły',
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
    DemandAnswer.objects.create(demand=demand, author=request.user.profile, text='Zrobione!')

    subject = f"[RPG] Dezyderat nr {demand.id}"
    message = f"{request.user.profile} oznaczył dezyderat jako 'zrobiony'.\n" \
              f"Dezyderat:\n{demand.text}\n" \
              f"{request.get_host()}/contact/demands/detail:{demand.id}/\n\n"
    sender = settings.EMAIL_HOST_USER
    if request.user.profile.character_status == 'active_player':
        receivers = ['lukas.kozicki@gmail.com']
    else:
        receivers = [demand.author.user.email]
    send_mail(subject, message, sender, receivers)

    messages.info(request, 'Oznaczono jako zrobiony!')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def mark_done_and_answer_view(request, demand_id):
    demand = get_object_or_404(Demand, id=demand_id)

    if request.method == 'POST':
        form = DemandAnswerForm(request.POST or None, request.FILES)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.demand = demand
            answer.author = request.user.profile
            answer.save()

            demand.is_done = True
            demand.date_done = timezone.now()
            demand.save()

            subject = f"[RPG] Dezyderat nr {demand.id}"
            message = f"Dezyderat 'zrobiony' + odpowiedź:\n{answer.text}\n" \
                      f"{request.get_host()}/contact/demands/detail:{demand.id}/\n\n"
            sender = settings.EMAIL_HOST_USER
            receivers = [demand.author.user.email]
            send_mail(subject, message, sender, receivers)

            messages.info(request, 'Oznaczono dezyderat jako zrobiony i wysłano odpowiedź!')
            return redirect('contact:main')
    else:
        form = DemandAnswerForm()

    context = {
        'page_title': 'Odpowiedź na dezyderat',
        'demand': demand,
        'form': form
    }
    return render(request, 'contact/answer.html', context)


@login_required
def mark_undone_view(request, demand_id):
    demand = get_object_or_404(Demand, id=demand_id)
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
        receivers = [demand.author.user.email]
    send_mail(subject, message, sender, receivers)

    messages.info(request, 'Oznaczono jako niezrobiony!')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
