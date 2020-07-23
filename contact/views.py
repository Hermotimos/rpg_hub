from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from contact.forms import (DemandsCreateForm, DemandAnswerForm,
                           PlansCreateForm, PlansModifyForm)
from contact.models import Demand, DemandAnswer, Plan
from rpg_project.utils import send_emails
from rules.models import Skill, Synergy, WeaponType, PlateType
from users.models import User


# ----------------------------- DEMANDS -----------------------------


@login_required
def demands_main_view(request):
    user = request.user
    ds = Demand.objects.all().\
        select_related('author__profile', 'addressee__profile').\
        prefetch_related('demand_answers__author__profile')
    
    # excludes necessery to filter out plans (Demands sent to oneself)
    received_u = ds.filter(is_done=False, addressee=user).exclude(author=user)
    received_d = ds.filter(is_done=True, addressee=user).exclude(author=user)
    sent_u = ds.filter(is_done=False, author=user).exclude(addressee=user)
    sent_d = ds.filter(is_done=True, author=user).exclude(addressee=user)

    if request.method == 'POST':
        form = DemandAnswerForm(request.POST, request.FILES)
        if form.is_valid():
            id_ = request.POST.get('form_id')
            demand = Demand.objects.get(id=id_)
            answer = form.save(commit=False)
            answer.demand = demand
            answer.author = request.user
            answer.save()
    
            if user == demand.author:
                informed_ids = [demand.addressee.profile.id]
            else:
                informed_ids = [demand.author.profile.id]
    
            send_emails(request, informed_ids, demand_answer=answer)
            messages.info(request, 'Dodano odpowiedź!')
            return redirect('contact:demands-main')
    else:
        form = DemandAnswerForm()
    
    context = {
        'page_title': 'Dezyderaty',
        'received_undone': received_u,
        'received_done': received_d,
        'sent_undone': sent_u,
        'sent_done': sent_d,
        'form': form,
    }
    return render(request, 'contact/demands_main.html', context)



@login_required
def demands_create_view(request):
    if request.method == 'POST':
        form = DemandsCreateForm(authenticated_user=request.user, data=request.POST, files=request.FILES)
        if form.is_valid():
            demand = form.save(commit=False)
            demand.author = request.user
            demand.save()

            subject = f"[RPG] Dezyderat {demand.id} [nowy]"
            message = f"Dezyderat od {demand.author}:\n{demand.text}\n" \
                      f"{request.get_host()}/contact/demands/detail:{demand.id}/\n\n"
            sender = settings.EMAIL_HOST_USER
            receivers = [demand.addressee.email]
            send_mail(subject, message, sender, receivers)

            messages.info(request, 'Dezyderat został wysłany!')
            _next = request.POST.get('next', '/')
            return HttpResponseRedirect(_next)
    else:
        form = DemandsCreateForm(authenticated_user=request.user)

    context = {
        'page_title': 'Nowy dezyderat',
        'form': form,
    }
    return render(request, 'contact/demands_create.html', context)



@login_required
def demands_delete_view(request, demand_id):
    demand = get_object_or_404(Demand, id=demand_id)
    if request.user == demand.author:
        demand.delete()
        messages.info(request, 'Usunięto dezyderat!')
        return redirect('contact:demands-main')
        # return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        return redirect('home:dupa')



@login_required
def demands_detail_view(request, demand_id):
    demand = get_object_or_404(Demand, id=demand_id)
    answers = DemandAnswer.objects.filter(demand=demand).select_related('author__profile').order_by('date_posted')

    if request.method == 'POST':
        form = DemandAnswerForm(request.POST, request.FILES)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.demand = demand
            answer.author = request.user
            answer.save()

            subject = f"[RPG] Dezyderat nr {demand.id}"
            message = f"Odpowiedź od {answer.author}:\n{answer.text}\n" \
                      f"{request.get_host()}/contact/demands/detail:{demand.id}/\n\n"
            sender = settings.EMAIL_HOST_USER
            if request.user == demand.author:
                receivers = [demand.addressee.email]
            else:
                receivers = [demand.author.email]
            send_mail(subject, message, sender, receivers)

            messages.info(request, 'Dodano odpowiedź!')
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
        return render(request, 'contact/demands_detail.html', context)
    else:
        return redirect('home:dupa')



@login_required
def mark_done_view(request, demand_id):
    demand = get_object_or_404(Demand, id=demand_id)
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
        if request.user == demand.author:
            receivers = [demand.addressee.email]
        else:
            receivers = [demand.author.email]
        send_mail(subject, message, sender, receivers)

        messages.info(request, 'Oznaczono jako zrobiony!')
        return redirect('contact:demands-main')

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
        if request.user == demand.author:
            receivers = [demand.addressee.email]
        else:
            receivers = [demand.author.email]
        send_mail(subject, message, sender, receivers)

        messages.info(request, 'Oznaczono jako niezrobiony!')
        return redirect('contact:demands-main')

    else:
        return redirect('home:dupa')


# ----------------------------- PLANS -----------------------------



@login_required
def plans_main_view(request):
    user = request.user
    profile = user.profile
    plans = Plan.objects.filter(author=user).select_related('author__profile')

    if profile.status == 'gm':
        models = [Skill, Synergy, WeaponType, PlateType]
        # Objs known to no profile: {'model_1': [obj1, obj2], model_2: [obj1]}
        todos = {}
        for m in models:
            todos[f'{m._meta.verbose_name_plural}'] = \
                m.objects.annotate(cnt=Count('allowed_profiles')).filter(cnt=0)
    
        text = '=>Do uzupełnienia:\n\n '
        create_todo = False
        for cnt, (model_name, objs) in enumerate(todos.items()):
            text += f'{cnt}) {model_name} z 0 allowed_profiles:\n' \
                    f'{[str(o) for o in objs] if objs else ""}\n\n'
            if objs:
                create_todo = True
                
        if create_todo:
            Plan.objects.update_or_create(
                text__contains='=>Do uzupełnienia:',
                defaults={'text': text, 'author': request.user}
            )
        else:
            try:
                Plan.objects.get(text__contains='=>Do uzupełnienia:').delete()
            except Plan.DoesNotExist:
                pass
    
    context = {
        'page_title': 'Plany',
        'plans': plans,
    }
    return render(request, 'contact/plans_main.html', context)



@login_required
def plans_for_gm_view(request):
    context = {
        'page_title': 'Plany graczy',
        'plans': Plan.objects.filter(inform_gm=True).select_related('author__profile'),
    }
    if request.user.profile.status == 'gm':
        return render(request, 'contact/plans_for_gm.html', context)
    else:
        return redirect('home:dupa')



@login_required
def plans_create_view(request):
    if request.method == 'POST':
        form = PlansCreateForm(request.POST, request.FILES)
        if form.is_valid():
            plan = form.save(commit=False)
            plan.author = request.user
            plan.addressee = request.user
            plan.save()

            if plan.inform_gm:
                subject = f"[RPG] Info o planach od {request.user.profile}"
                message = f"{request.user.profile} poinformował o swoich planach:\n\n{plan.text}\n" \
                          f"{request.get_host()}/contact/plans/for-gm/\n\n"
                sender = settings.EMAIL_HOST_USER
                receivers = ['lukas.kozicki@gmail.com']
                send_mail(subject, message, sender, receivers)

            messages.info(request, f'Plan został zapisany!')
            _next = request.POST.get('next', '/')
            return HttpResponseRedirect(_next)
    else:
        form = PlansCreateForm()

    context = {
        'page_title': 'Nowy plan',
        'form': form,
    }
    return render(request, 'contact/plans_create.html', context)



@login_required
def plans_delete_view(request, plan_id):
    plan = get_object_or_404(Plan, id=plan_id)
    if request.user == plan.author:
        plan.delete()
        messages.info(request, 'Usunięto plan!')
        return redirect('contact:plans-main')
        # return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        return redirect('home:dupa')



@login_required
def plans_modify_view(request, plan_id):
    plan = get_object_or_404(Plan, id=plan_id)
    if request.method == 'POST':
        form = PlansModifyForm(instance=plan, data=request.POST, files=request.FILES)
        if form.is_valid():
            plan = form.save()

            if plan.inform_gm:
                subject = f"[RPG] Info o zmianie planów od {request.user.profile}"
                message = f"{request.user.profile} poinformował o zmianie planów:\n\n{plan.text}\n" \
                    f"{request.get_host()}/contact/plans/for-gm/\n\n"
                sender = settings.EMAIL_HOST_USER
                receivers = ['lukas.kozicki@gmail.com']
                send_mail(subject, message, sender, receivers)

            messages.info(request, 'Zmodyfikowano plan!')
            _next = request.POST.get('next', '/')
            return HttpResponseRedirect(_next)
    else:
        form = PlansModifyForm(instance=plan)

    context = {
        'page_title': 'Zmiana planów?',
        'form': form
    }
    if request.user == plan.author:
        return render(request, 'contact/plans_modify.html', context)
    else:
        return redirect('home:dupa')
