from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from contact.forms import DemandsCreateForm, DemandsModifyForm, DemandAnswerForm, PlansCreateForm, PlansModifyForm
from contact.models import Demand, DemandAnswer, Plan
from rpg_project.utils import query_debugger
from rules.models import Skill, Synergy, WeaponType, PlateType
from users.models import User


# ----------------------------- DEMANDS -----------------------------


@query_debugger
@login_required
def demands_main_view(request):
    received_undone = Demand.objects.filter(is_done=False, addressee=request.user).exclude(author=request.user).\
        select_related('author__profile', 'addressee__profile')
    received_done = Demand.objects.filter(is_done=True, addressee=request.user).exclude(author=request.user).\
        select_related('author__profile', 'addressee__profile')
    sent_undone = Demand.objects.filter(is_done=False, author=request.user).exclude(addressee=request.user).\
        select_related('author__profile', 'addressee__profile')
    sent_done = Demand.objects.filter(is_done=True, author=request.user).exclude(addressee=request.user).\
        select_related('author__profile', 'addressee__profile')

    context = {
        'page_title': 'Dezyderaty',
        'received_undone': received_undone,
        'received_done': received_done,
        'sent_undone': sent_undone,
        'sent_done': sent_done
    }
    return render(request, 'contact/demands_main.html', context)


@query_debugger
@login_required
def demands_create_view(request):
    if request.method == 'POST':
        form = DemandsCreateForm(authenticated_user=request.user, data=request.POST, files=request.FILES)
        if form.is_valid():
            demand = form.save(commit=False)
            demand.author = request.user
            demand.save()

            subject = f"[RPG] Dezyderat nr {demand.id}"
            message = f"Dezyderat od {demand.author}:\n{demand.text}\n" \
                      f"{request.get_host()}/contact/demands/detail:{demand.id}/\n\n"
            sender = settings.EMAIL_HOST_USER
            receivers = [demand.addressee.email]
            send_mail(subject, message, sender, receivers)

            messages.info(request, f'Dezyderat został wysłany!')
            _next = request.POST.get('next', '/')
            return HttpResponseRedirect(_next)
    else:
        form = DemandsCreateForm(authenticated_user=request.user)

    context = {
        'page_title': 'Nowy dezyderat',
        'form': form,
    }
    return render(request, 'contact/demands_create.html', context)


@query_debugger
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


@query_debugger
@login_required
def demands_modify_view(request, demand_id):
    demand = get_object_or_404(Demand, id=demand_id)

    if request.method == 'POST':
        form = DemandsModifyForm(instance=demand, data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save()

            subject = f"[RPG] Dezyderat nr {demand.id}"
            message = f"Modyfikacja przez {demand.author}:\n{demand.text}\n" \
                      f"{request.get_host()}/contact/demands/detail:{demand.id}/\n\n"
            sender = settings.EMAIL_HOST_USER
            receivers = [demand.addressee.email]
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
        return render(request, 'contact/demands_modify.html', context)
    else:
        return redirect('home:dupa')


@query_debugger
@login_required
def demands_detail_view(request, demand_id):
    demand = get_object_or_404(Demand, id=demand_id)
    answers = DemandAnswer.objects.filter(demand=demand).select_related('author', 'author__profile')

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
        return render(request, 'contact/demands_detail.html', context)
    else:
        return redirect('home:dupa')


@query_debugger
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


@query_debugger
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


@query_debugger
@login_required
def plans_main_view(request):

    skills_no_allowed = Skill.objects.annotate(num_allowed=Count('allowed_profiles')).filter(num_allowed=0)
    skills_to_do = [s.name for s in skills_no_allowed]
    synergies_no_allowed = Synergy.objects.annotate(num_allowed=Count('allowed_profiles')).filter(num_allowed=0)
    synergies_to_do = [s.name for s in synergies_no_allowed]

    weapon_types_no_allowed = WeaponType.objects.annotate(num_allowed=Count('allowed_profiles')).filter(num_allowed=0)
    weapon_types_to_do = [wt.name for wt in weapon_types_no_allowed]
    plate_types_no_allowed = PlateType.objects.annotate(num_allowed=Count('allowed_profiles')).filter(num_allowed=0)
    plate_types_to_do = [pt.name for pt in plate_types_no_allowed]

    text = \
        f'=>Lista rzeczy do uzupełnienia:\n ' \
        f'1) Skille z 0 allowed_profiles:\n{[s for s in skills_to_do] if skills_to_do else 0}\n' \
        f'2) Synergie z 0 allowed_profiles:\n{[s for s in synergies_to_do] if synergies_to_do else 0}\n' \
        f'3) Bronie z 0 allowed_profiles:\n{[s for s in weapon_types_to_do] if weapon_types_to_do else 0}\n' \
        f'4) Zbroje z 0 allowed_profiles:\n{[s for s in plate_types_to_do] if plate_types_to_do else 0}\n'

    if skills_to_do or synergies_to_do or weapon_types_to_do or plate_types_to_do:
        try:
            todos = Plan.objects.get(text__contains='=>Lista rzeczy do uzupełnienia')
            todos.text = text
        except Plan.DoesNotExist:
            Plan.objects.create(text=text, author=User.objects.get(profile__character_status='gm'))
    else:
        try:
            Plan.objects.get(text__contains='=>Lista rzeczy do uzupełnienia').delete()
        except Plan.DoesNotExist:
            pass

    plans = list(Plan.objects.filter(author=request.user))
    context = {
        'page_title': 'Plany',
        'plans': plans,
    }
    return render(request, 'contact/plans_main.html', context)


@query_debugger
@login_required
def plans_for_gm_view(request):
    plans = list(Plan.objects.filter(inform_gm=True))
    context = {
        'page_title': 'Plany graczy',
        'plans': plans,
    }
    if request.user.profile.character_status == 'gm':
        return render(request, 'contact/plans_for_gm.html', context)
    else:
        return redirect('home:dupa')


@query_debugger
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


@query_debugger
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


@query_debugger
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
                    f"{request.get_host()}/contact/demands/for-gm/\n\n"
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
