from io import BytesIO, StringIO
from django.http import HttpResponse
from django.template.loader import get_template
from django.conf import settings

import os
from xhtml2pdf import pisa


def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(html, result, path=os.path.join(settings.STATIC_ROOT, '/fonts/'))
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None
