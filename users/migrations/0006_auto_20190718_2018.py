# Generated by Django 2.2.1 on 2019-07-18 18:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_auto_20190718_2018'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='profile',
            options={'ordering': ['character_status', 'character_name']},
        ),
        migrations.AlterField(
            model_name='profile',
            name='character_status',
            field=models.CharField(choices=[('active_player', 'Gracz'), ('inactive_player', 'Dawny gracz'), ('npc', 'Bohater niezależny'), ('gm', 'Mistrz gry')], default='npc', max_length=20),
        ),
    ]
