from django.http import HttpResponse
from django.template.loader import get_template
from rules.utils import render_to_pdf, link_callback
from django.template import Context
from xhtml2pdf import pisa


def generate_pdf_view(request, *args, **kwargs):
    template = get_template('rules/combat.html')
    context = {
        'page_title': 'Przebieg walki'
    }
    html = template.render(context)
    pdf = render_to_pdf('rules/combat.html', context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = 'Zasady-2.2.Przebieg-walki.pdf'          # short title, no '_' or ' ' otherwise gives random title
        content = f'attachment; filename={filename}'
        response['Content-Disposition'] = content
        return response
    HttpResponse('Wystąpił problem...')


def render_pdf_view(request):
    context = {
        'page_title': 'Przebieg walki'
    }

    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'

    # find the template and render it.
    template = get_template('rules/combat.html')
    html = template.render(Context(context))

    # create a pdf
    pisaStatus = pisa.CreatePDF(html, dest=response, link_callback=link_callback)

    # if error then show some funy view
    if pisaStatus.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response
