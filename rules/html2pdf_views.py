#! /usr/bin/python
# -*- encoding: utf-8 -*-

from django.http import HttpResponse
from django.template.loader import get_template
from rules.utils import render_to_pdf
from xhtml2pdf import pisa
from io import BytesIO, StringIO
from django.conf import settings


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


def generate_pdf_view_2(request):
    template = get_template('rules/combat.html')
    context = {
        'page_title': 'Przebieg walki'
    }
    html = template.render(context)
    result = BytesIO()
    pdf = pisa.pisaDocument(StringIO(html), result)
    # other options, work the same, supposedly serve fonts but they don't:
    # pdf = pisa.pisaDocument(StringIO(html), result, encoding='UTF-8')
    # pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result, encoding='UTF-8')
    # pdf = pisa.pisaDocument(StringIO(html), result, path=os.path.join(settings.STATIC_ROOT, '/fonts/'))
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return HttpResponse('We had some errors<pre>%s</pre>' % html.escape(html))






