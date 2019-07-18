from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.mail import send_mail
from report.forms import ReportForm


@login_required
def report_view(request):
    if request.method == 'POST':
        report_form = ReportForm(request.POST or None)
        if report_form.is_valid():

            subject = f"[RPG] Problem"
            message = f"{request.user.profile} zgłasza problem:\n" \
                      f"Zgłoszenie:\n{report_form.cleaned_data['text']}"
            sender = settings.EMAIL_HOST_USER
            receivers_list = ['lukas.kozicki@gmail.com']
            send_mail(subject, message, sender, receivers_list)

            messages.info(request, f'MG został poinformowany o problemie!')
            return redirect('profile')
    else:
        report_form = ReportForm()

    context = {
        'page_title': 'Zgłoś problem',
        'report_form': report_form,
    }
    return render(request, 'report/report.html', context)
