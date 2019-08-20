from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.mail import send_mail
from contact.models import Report
from contact.forms import ReportForm


@login_required
def report_view(request):
    if request.method == 'POST':
        form = ReportForm(request.POST or None)
        if form.is_valid():
            report = form.save(commit=False)
            report.author = request.user
            report.save()

            subject = f"[RPG] Problem"
            message = f"{request.user.profile} zgłasza problem:\n" \
                      f"Zgłoszenie:\n{form.cleaned_data['text']}"
            sender = settings.EMAIL_HOST_USER
            receivers_list = ['lukas.kozicki@gmail.com']
            send_mail(subject, message, sender, receivers_list)

            messages.info(request, f'MG został poinformowany o problemie!')
            return redirect('users:profile')
    else:
        form = ReportForm()

    context = {
        'page_title': 'Zgłoś problem',
        'form': form,
    }
    return render(request, 'contact/report.html', context)


def reports_list_view(request):
    reports_undone = Report.objects.filter(is_done=False)
    reports_done = Report.objects.filter(is_done=True)

    context = {
        'page_title': 'Zgłoszone problemy',
        'reports_undone': reports_undone,
        'reports_done': reports_done
    }
    return render(request, 'contact/reports_list.html', context)


def mark_done_view(request):
    pass

def mark_undone_view(request):
    pass