from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.mail import send_mail
from contact.forms import ReportForm


@login_required
def report_view(request):
    if request.method == 'POST':
        form = ReportForm(request.POST or None)
        if form.is_valid():

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
    return render(request, 'report/report.html', context)
