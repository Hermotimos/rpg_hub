# Generated by Django 3.1 on 2020-12-28 20:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20201225_1757'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('debates', '0002_auto_20201228_2101'),
    ]

    operations = [
        migrations.AlterField(
            model_name='debate',
            name='known_directly',
            field=models.ManyToManyField(help_text='\n            1) Włączaj tylko postacie znajdujące się w pobliżu w chwili\n                zakończenia ostatniej sesji.<br>\n            2) Postacie będące w pobliżu, ale nie włączone do narady, mogą to zauważyć.<br>\n            3) Jeśli chcesz zaczekać na sposobny moment, powiadom MG.<br>\n            4) Jeśli chcesz się naradzić z postacią, której nie ma na liście, powiadom MG.<br>\n        ', limit_choices_to=models.Q(status__in=['active_player', 'inactive_player', 'living_npc']), related_name='debates_known_directly', to='users.Profile', verbose_name='Uczestnicy'),
        ),
        migrations.AlterField(
            model_name='debate',
            name='name',
            field=models.CharField(max_length=77, unique=True, verbose_name='Tytuł narady'),
        ),
        migrations.AlterField(
            model_name='remark',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='remarks', to=settings.AUTH_USER_MODEL, verbose_name='Autor'),
        ),
        migrations.AlterField(
            model_name='topic',
            name='title',
            field=models.CharField(max_length=77, unique=True, verbose_name='Temat narad'),
        ),
    ]