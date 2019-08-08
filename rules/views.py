from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def rules_main_view(request):

    context = {
        'page_title': 'Zasady'
    }
    return render(request, 'rules/main.html', context)

