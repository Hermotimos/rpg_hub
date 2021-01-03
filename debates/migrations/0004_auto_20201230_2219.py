# Generated by Django 3.1 on 2020-12-30 21:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20201225_1757'),
        ('debates', '0003_auto_20201228_2126'),
    ]

    operations = [
        migrations.AlterField(
            model_name='debate',
            name='known_directly',
            field=models.ManyToManyField(help_text='\n            ***Aby zaznaczyć wiele postaci - użyj CTRL albo SHIFT.<br><br>\n            1) Włączaj tylko postacie znajdujące się w pobliżu w chwili\n                zakończenia ostatniej sesji.<br>\n            2) Postacie w pobliżu niewłączone do narady mogą to zauważyć.<br>\n            3) Jeśli chcesz zaczekać na sposobny moment, powiadom MG.<br>\n            4) Jeśli na liście brakuje postaci, powiadom MG.<br><br>\n        ', limit_choices_to=models.Q(status__in=['active_player', 'inactive_player', 'living_npc']), related_name='debates_known_directly', to='users.Profile', verbose_name='Uczestnicy'),
        ),
        migrations.AlterField(
            model_name='remark',
            name='text',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='topic',
            name='title',
            field=models.CharField(max_length=77, unique=True, verbose_name='Temat narady'),
        ),
    ]