from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from contact.forms import (DemandsCreateForm, DemandAnswerForm, PlanForm)
from contact.models import Demand, DemandAnswer, Plan
from rpg_project.utils import send_emails
from rules.models import Skill, Synergy, Weapon, Plate


# ----------------------------- DEMANDS -----------------------------


@login_required
def demands_main_view(request):
    profile = request.user.profile
    ds = Demand.objects.all().\
        select_related('author', 'addressee').\
        prefetch_related('demand_answers__author')
    
    # excludes necessery to filter out plans (Demands sent to oneself)
    received_u = ds.filter(is_done=False, addressee=profile).exclude(author=profile)
    received_d = ds.filter(is_done=True, addressee=profile).exclude(author=profile)
    sent_u = ds.filter(is_done=False, author=profile).exclude(addressee=profile)
    sent_d = ds.filter(is_done=True, author=profile).exclude(addressee=profile)

    if request.method == 'POST':
        form = DemandAnswerForm(request.POST, request.FILES)
        if form.is_valid():
            id_ = request.POST.get('form_id')
            demand = Demand.objects.get(id=id_)
            answer = form.save(commit=False)
            answer.demand = demand
            answer.author = profile
            answer.save()
    
            if profile == demand.author:
                informed_ids = [demand.addressee.id]
            else:
                informed_ids = [demand.author.id]
    
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
    profile = request.user.profile
    
    if request.method == 'POST':
        form = DemandsCreateForm(authenticated_user=request.user, data=request.POST, files=request.FILES)
        if form.is_valid():
            demand = form.save(commit=False)
            demand.author = profile
            demand.save()

            subject = f"[RPG] Dezyderat {demand.id} [nowy]"
            message = f"Dezyderat od {demand.author}:\n{demand.text}\n" \
                      f"{request.get_host()}/contact/demands/detail:{demand.id}/\n\n"
            sender = settings.EMAIL_HOST_USER
            receivers = [demand.addressee.user.email]
            send_mail(subject, message, sender, receivers)
            messages.info(request, 'Dezyderat został wysłany!')
            return redirect('contact:demands-main')
    else:
        form = DemandsCreateForm(authenticated_user=request.user)

    context = {
        'page_title': 'Nowy dezyderat',
        'form': form,
    }
    return render(request, '_form.html', context)


@login_required
def demands_delete_view(request, demand_id):
    profile = request.user.profile
    demand = get_object_or_404(Demand, id=demand_id)
    
    if profile == demand.author:
        demand.delete()
        messages.info(request, 'Usunięto dezyderat!')
        return redirect('contact:demands-main')
    else:
        return redirect('home:dupa')


@login_required
def demands_detail_view(request, demand_id):
    profile = request.user.profile
    demand = get_object_or_404(Demand, id=demand_id)
    answers = DemandAnswer.objects.filter(demand=demand).select_related('author').order_by('date_posted')

    if request.method == 'POST':
        form = DemandAnswerForm(request.POST, request.FILES)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.demand = demand
            answer.author = profile
            answer.save()

            subject = f"[RPG] Dezyderat nr {demand.id}"
            message = f"Odpowiedź od {answer.author}:\n{answer.text}\n" \
                      f"{request.get_host()}/contact/demands/detail:{demand.id}/\n\n"
            sender = settings.EMAIL_HOST_USER
            if profile == demand.author:
                receivers = [demand.addressee.user.email]
            else:
                receivers = [demand.author.user.email]
            send_mail(subject, message, sender, receivers)

            messages.info(request, 'Dodano odpowiedź!')
            return redirect('contact:demands-main')
    else:
        form = DemandAnswerForm()

    context = {
        'page_title': 'Dezyderat - szczegóły',
        'demand': demand,
        'answers': answers,
        'form': form
    }
    if profile in [demand.author, demand.addressee]:
        return render(request, 'contact/demands_detail.html', context)
    else:
        return redirect('home:dupa')


@login_required
def mark_done_view(request, demand_id):
    profile = request.user.profile
    demand = get_object_or_404(Demand, id=demand_id)
    
    if profile in [demand.author, demand.addressee]:
        demand.is_done = True
        demand.date_done = timezone.now()
        demand.save()
        DemandAnswer.objects.create(demand=demand, author=profile, text='Zrobione!')

        subject = f"[RPG] Dezyderat nr {demand.id}"
        message = f"{profile} oznaczył dezyderat jako 'zrobiony'.\n" \
                  f"Dezyderat:\n{demand.text}\n" \
                  f"{request.get_host()}/contact/demands/detail:{demand.id}/\n\n"
        sender = settings.EMAIL_HOST_USER
        if profile == demand.author:
            receivers = [demand.addressee.user.email]
        else:
            receivers = [demand.author.user.email]
        send_mail(subject, message, sender, receivers)

        messages.info(request, 'Oznaczono jako zrobiony!')
        return redirect('contact:demands-main')

    else:
        return redirect('home:dupa')


@login_required
def mark_undone_view(request, demand_id):
    profile = request.user.profile
    demand = get_object_or_404(Demand, id=demand_id)
    
    if profile in [demand.author, demand.addressee]:
        demand.is_done = False
        demand.save()

        subject = f"[RPG] Dezyderat nr {demand.id}"
        message = f"{profile} cofnął dezyderat jako 'NIE-zrobiony'.\n" \
                  f"Dezyderat:\n{demand.text}\n" \
                  f"{request.get_host()}/contact/demands/detail:{demand.id}/\n\n"
        sender = settings.EMAIL_HOST_USER
        if profile == demand.author:
            receivers = [demand.addressee.user.email]
        else:
            receivers = [demand.author.user.email]
        send_mail(subject, message, sender, receivers)

        messages.info(request, 'Oznaczono jako niezrobiony!')
        return redirect('contact:demands-main')

    else:
        return redirect('home:dupa')


# ----------------------------- PLANS -----------------------------


@login_required
def plans_main_view(request):
    profile = request.user.profile
    plans = Plan.objects.filter(author=profile).select_related('author')

    if profile.status == 'gm':
        models = [Skill, Synergy, Weapon, Plate]
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
                defaults={'text': text, 'author': profile}
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
    profile = request.user.profile
    context = {
        'page_title': 'Plany graczy',
        'plans': Plan.objects.filter(inform_gm=True).select_related('author'),
    }
    if profile.status == 'gm':
        return render(request, 'contact/plans_for_gm.html', context)
    else:
        return redirect('home:dupa')


@login_required
def plans_create_view(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = PlanForm(request.POST, request.FILES)
        if form.is_valid():
            plan = form.save(commit=False)
            plan.author = profile
            plan.addressee = profile
            plan.save()

            if plan.inform_gm:
                subject = f"[RPG] Info o planach od {profile}"
                message = f"{profile} poinformował o swoich planach:\n\n{plan.text}\n" \
                          f"{request.get_host()}/contact/plans/for-gm/\n\n"
                sender = settings.EMAIL_HOST_USER
                receivers = ['lukas.kozicki@gmail.com']
                send_mail(subject, message, sender, receivers)

            messages.info(request, f'Plan został zapisany!')
            return redirect('contact:plans-main')
    else:
        form = PlanForm()

    context = {
        'page_title': 'Nowy plan',
        'form': form,
    }
    return render(request, '_form.html', context)


@login_required
def plans_delete_view(request, plan_id):
    profile = request.user.profile
    plan = get_object_or_404(Plan, id=plan_id)
    
    if profile == plan.author:
        plan.delete()
        messages.info(request, 'Usunięto plan!')
        return redirect('contact:plans-main')
    else:
        return redirect('home:dupa')


@login_required
def plans_modify_view(request, plan_id):
    profile = request.user.profile
    plan = get_object_or_404(Plan, id=plan_id)
    
    if request.method == 'POST':
        form = PlanForm(instance=plan, data=request.POST, files=request.FILES)
        if form.is_valid():
            plan = form.save()
            if plan.inform_gm:
                subject = f"[RPG] Info o zmianie planów od {profile}"
                message = f"{profile} poinformował o zmianie planów:\n\n{plan.text}\n" \
                    f"{request.get_host()}/contact/plans/for-gm/\n\n"
                sender = settings.EMAIL_HOST_USER
                receivers = ['lukas.kozicki@gmail.com']
                send_mail(subject, message, sender, receivers)

            messages.info(request, 'Zmodyfikowano plan!')
            return redirect('contact:plans-main')
    else:
        form = PlanForm(instance=plan)

    context = {
        'page_title': 'Zmiana planów?',
        'form': form,
    }
    if profile == plan.author:
        return render(request, '_form.html', context)
    else:
        return redirect('home:dupa')
