from django.http import HttpResponse
from django.template.loader import get_template
from rules.utils import render_to_pdf


def generate_pdf_view(request, *args, **kwargs):
    template = get_template('rules/combat.html')
    context = {
        'page_title': 'Przebieg walki'
    }
    html = template.render(context)
    pdf = render_to_pdf('rules/combat.html', context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = 'Zasady 2.2. Przebieg walki.pdf'          # short title, no '_' or gives random title
        content = f'attachment; filename={filename}'
        response['Content-Disposition'] = content
        return response
    HttpResponse('Wystąpił problem...')
