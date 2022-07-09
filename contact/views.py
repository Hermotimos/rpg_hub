from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from contact.forms import (DemandsCreateForm, DemandAnswerForm, PlanForm)
from contact.models import Demand, DemandAnswer, Plan
from rpg_project.utils import send_emails, auth_profile
from rules.models import Skill, WeaponType, Plate


# ----------------------------- DEMANDS -----------------------------


@login_required
@auth_profile(['all'])
def demands_main_view(request):
    current_profile = request.current_profile
    
    demands = Demand.objects.select_related('author__user', 'addressee__user')
    demands = demands.prefetch_related('demand_answers__author')
    
    # excludes necessery to filter out plans (Demands sent to oneself)
    received_u = demands.filter(is_done=False, addressee=current_profile).exclude(author=current_profile)
    received_d = demands.filter(is_done=True, addressee=current_profile).exclude(author=current_profile)
    sent_u = demands.filter(is_done=False, author=current_profile).exclude(addressee=current_profile)
    sent_d = demands.filter(is_done=True, author=current_profile).exclude(addressee=current_profile)

    if request.method == 'POST':
        form = DemandAnswerForm(request.POST, request.FILES)
        if form.is_valid():
            id_ = request.POST.get('form_id')
            demand = Demand.objects.get(id=id_)
            answer = form.save(commit=False)
            answer.demand = demand
            answer.author = current_profile
            answer.save()
    
            if current_profile == demand.author:
                informed_ids = [demand.addressee.id]
            else:
                informed_ids = [demand.author.id]
            send_emails(request, informed_ids, demand_answer=answer)
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
@auth_profile(['all'])
def demands_create_view(request):
    current_profile = request.current_profile
    
    if request.method == 'POST':
        form = DemandsCreateForm(
            profile=current_profile, data=request.POST, files=request.FILES)
        
        if form.is_valid():
            demand = form.save(commit=False)
            demand.author = current_profile
            demand.save()

            informed_ids = [demand.addressee.id]
            send_emails(request, informed_ids, demand=demand)
            return redirect('contact:demands-main')
    else:
        form = DemandsCreateForm(profile=current_profile)

    context = {
        'page_title': 'Nowy dezyderat',
        'form': form,
    }
    return render(request, '_form.html', context)


@login_required
@auth_profile(['all'])
def demands_delete_view(request, demand_id):
    current_profile = request.current_profile
    demand = get_object_or_404(Demand, id=demand_id)
    if current_profile == demand.author:
        demand.delete()
        messages.info(request, 'Usunięto dezyderat!')
        return redirect('contact:demands-main')
    else:
        return redirect('users:dupa')


@login_required
@auth_profile(['all'])
def demands_detail_view(request, demand_id):
    current_profile = request.current_profile
    
    demand = get_object_or_404(Demand, id=demand_id)
    answers = DemandAnswer.objects.filter(demand=demand).select_related('author').order_by('date_posted')

    if request.method == 'POST':
        form = DemandAnswerForm(request.POST, request.FILES)
        
        if form.is_valid():
            answer = form.save(commit=False)
            answer.demand = demand
            answer.author = current_profile
            answer.save()

            if current_profile == demand.author:
                informed_ids = [demand.addressee.id]
            else:
                informed_ids = [demand.author.id]
            send_emails(request, informed_ids, demand_answer=answer)
            return redirect('contact:demands-main')
    else:
        form = DemandAnswerForm()

    context = {
        'page_title': 'Dezyderat - szczegóły',
        'demand': demand,
        'answers': answers,
        'form': form
    }
    if current_profile in [demand.author, demand.addressee]:
        return render(request, 'contact/demands_detail.html', context)
    else:
        return redirect('users:dupa')


@login_required
@auth_profile(['all'])
def demand_done_undone_view(request, demand_id, is_done):
    current_profile = request.current_profile
    
    demand = get_object_or_404(Demand, id=demand_id)
    
    if current_profile in [demand.author, demand.addressee]:
        demand.is_done = is_done
        if is_done:
            demand.date_done = timezone.now()
            demand.save()
            DemandAnswer.objects.create(
                demand=demand, author=current_profile, text='Zrobione!')
        demand.save()

        if current_profile == demand.author:
            informed_ids = [demand.addressee.id]
        else:
            informed_ids = [demand.author.id]
        send_emails(request, informed_ids, demand=demand, is_done=is_done)
        return redirect('contact:demands-main')

    else:
        return redirect('users:dupa')


# ----------------------------- PLANS -----------------------------


@login_required
@auth_profile(['all'])
def plans_main_view(request):
    current_profile = request.current_profile
    plans = Plan.objects.filter(author=current_profile).select_related('author')

    if current_profile.status == 'gm':
        models = [Skill, WeaponType, Plate]
        # Objs known to no profile: {'model_1': [obj1, obj2], model_2: [obj1]}
        todos = {}
        for m in models:
            todos[f'{m._meta.verbose_name_plural}'] = m.objects.annotate(cnt=Count('allowees')).filter(cnt=0)
    
        text = '=>Do uzupełnienia:\n\n '
        create_todo = False
        for cnt, (model_name, objs) in enumerate(todos.items()):
            text += f'{cnt}) {model_name} z 0 allowees:\n' \
                    f'{[str(o) for o in objs] if objs else ""}\n\n'
            if objs:
                create_todo = True
                
        if create_todo:
            Plan.objects.update_or_create(
                text__contains='=>Do uzupełnienia:',
                defaults={'text': text, 'author': current_profile}
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
@auth_profile(['gm', 'spectator'])
def plans_for_gm_view(request):
    context = {
        'page_title': 'Plany graczy',
        'plans': Plan.objects.filter(inform_gm=True).select_related('author'),
    }
    return render(request, 'contact/plans_for_gm.html', context)


@login_required
@auth_profile(['all'])
def plans_create_view(request):
    profile = request.current_profile
    
    if request.method == 'POST':
        form = PlanForm(request.POST, request.FILES)
        
        if form.is_valid():
            plan = form.save(commit=False)
            plan.author = profile
            plan.addressee = profile
            plan.save()

            if plan.inform_gm:
                send_emails(request, plan_created=plan)
            return redirect('contact:plans-main')
    else:
        form = PlanForm()

    context = {
        'page_title': 'Nowy plan',
        'form': form,
    }
    return render(request, '_form.html', context)


@login_required
@auth_profile(['all'])
def plans_delete_view(request, plan_id):
    profile = request.current_profile
    plan = get_object_or_404(Plan, id=plan_id)
    if profile == plan.author:
        plan.delete()
        messages.info(request, 'Usunięto plan!')
        return redirect('contact:plans-main')
    else:
        return redirect('users:dupa')


@login_required
@auth_profile(['all'])
def plans_modify_view(request, plan_id):
    profile = request.current_profile
    
    plan = get_object_or_404(Plan, id=plan_id)
    
    if request.method == 'POST':
        form = PlanForm(instance=plan, data=request.POST, files=request.FILES)
        
        if form.is_valid():
            plan = form.save()
            
            if plan.inform_gm:
                send_emails(request, plan_modified=plan)
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
        return redirect('users:dupa')
