

import pdfkit
config = pdfkit.configuration(wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')
# pdfkit.from_url('http://127.0.0.1:8000/rules/combat/', 'google.pdf', configuration=config)

options = {
    'font-family': 'IMFellGreatPrimer',
    'src': 'url(fonts/IMFellGreatPrimer-Regular.ttf)',
    'encoding': "UTF-8",

}

css = ['../static/css/main.css', '../static/css/rules.css']
pdfkit.from_file('./templates/rules/combat.html', 'out.pdf', configuration=config, css=css)