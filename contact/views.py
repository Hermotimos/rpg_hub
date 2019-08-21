from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.mail import send_mail
from contact.models import Demand
from contact.forms import ReportForm, ResponseForm


@login_required
def report_view(request):
    if request.method == 'POST':
        form = ReportForm(request.POST or None)
        if form.is_valid():
            report = form.save(commit=False)
            report.author = request.user
            report.save()

            if request.user.profile.character_status != 'gm':
                subject = f"[RPG] Zgłoszenie od {request.user.profile}"
                message = f"{request.user.profile} zgłasza:\n" \
                          f"{form.cleaned_data['text']}"
                sender = settings.EMAIL_HOST_USER
                receivers_list = ['lukas.kozicki@gmail.com']
                send_mail(subject, message, sender, receivers_list)

            messages.info(request, f'Zgłoszenie zostało wysłane!')
            return redirect('contact:reports-list')
    else:
        form = ReportForm()

    context = {
        'page_title': 'Zgłoszenie do MG',
        'form': form,
    }
    return render(request, 'contact/demand.html', context)


@login_required
def reports_list_view(request):
    if request.user.profile.character_status == 'gm':
        reports_undone = Demand.objects.filter(is_done=False)
        reports_done = Demand.objects.filter(is_done=True)
    else:
        reports_undone = Demand.objects.filter(is_done=False, author=request.user)
        reports_done = Demand.objects.filter(is_done=True, author=request.user)

    context = {
        'page_title': 'Zgłoszenia',
        'reports_undone': reports_undone,
        'reports_done': reports_done
    }
    return render(request, 'contact/demands_list.html', context)


@login_required
def mark_done_view(request, report_id):
    obj = Demand.objects.get(id=report_id)
    obj.is_done = True
    obj.response = 'Zrobione!'
    obj.save()
    messages.info(request, 'Oznaczono jako zrobione!')
    return redirect('contact:reports-list')


@login_required
def mark_done_and_respond_view(request, report_id):
    report = get_object_or_404(Demand, id=report_id)

    if request.method == 'POST':
        form = ResponseForm(instance=report, data=request.POST or None)
        if form.is_valid():
            report.is_done = True
            form.save()
            messages.info(request, 'Oznaczono jako zrobione!')
            return redirect('contact:reports-list')
    else:
        form = ResponseForm(instance=report)

    context = {
        'page_title': 'Odpowiedź na zgłoszenie',
        'report': report,
        'form': form
    }
    return render(request, 'contact/answer.html', context)


@login_required
def mark_undone_view(request, report_id):
    obj = Demand.objects.get(id=report_id)
    obj.is_done = False
    obj.save()
    messages.info(request, 'Oznaczono jako niezrobione!')
    return redirect('contact:reports-list')
