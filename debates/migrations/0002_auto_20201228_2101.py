# Generated by Django 3.1 on 2020-12-28 20:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20201225_1757'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('debates', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='debate',
            name='is_individual',
            field=models.BooleanField(verbose_name='Narada indywidualna?'),
        ),
        migrations.AlterField(
            model_name='debate',
            name='known_directly',
            field=models.ManyToManyField(limit_choices_to=models.Q(status__in=['active_player', 'inactive_player', 'living_npc']), related_name='debates_known_directly', to='users.Profile', verbose_name='Uczestnicy'),
        ),
        migrations.AlterField(
            model_name='debate',
            name='name',
            field=models.CharField(max_length=255, unique=True, verbose_name='Tytuł narady'),
        ),
        migrations.AlterField(
            model_name='remark',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='remarks', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='remark',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='post_pics', verbose_name='Obraz [opcjonalnie]'),
        ),
        migrations.AlterField(
            model_name='remark',
            name='text',
            field=models.TextField(verbose_name='Wypowiedź'),
        ),
        migrations.AlterField(
            model_name='topic',
            name='title',
            field=models.CharField(max_length=255, unique=True, verbose_name='Temat narad'),
        ),
    ]
