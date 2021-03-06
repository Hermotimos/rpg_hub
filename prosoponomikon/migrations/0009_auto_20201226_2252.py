# Generated by Django 3.1 on 2020-12-26 21:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('knowledge', '0003_auto_20201226_2252'),
        ('prosoponomikon', '0008_auto_20201226_1055'),
    ]

    operations = [
        migrations.AlterField(
            model_name='charactergroup',
            name='characters',
            field=models.ManyToManyField(related_name='character_groups', to='prosoponomikon.Character', verbose_name='Zgrupowane postacie'),
        ),
        migrations.AlterField(
            model_name='charactergroup',
            name='default_knowledge_packets',
            field=models.ManyToManyField(blank=True, related_name='character_group_defaults', to='knowledge.KnowledgePacket', verbose_name='Domyślne umiejętności zgrupowanych postaci'),
        ),
        migrations.AlterField(
            model_name='charactergroup',
            name='name',
            field=models.CharField(max_length=250, verbose_name='Nazwa grupy'),
        ),
        migrations.AlterField(
            model_name='charactergroup',
            name='order_no',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Numer porządkowy grupy [opcjonalnie]:'),
        ),
    ]
