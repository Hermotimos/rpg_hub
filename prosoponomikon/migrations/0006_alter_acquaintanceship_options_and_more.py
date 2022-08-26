# Generated by Django 4.0.4 on 2022-08-26 14:55

from django.db import migrations
import rpg_project.utils


class Migration(migrations.Migration):

    dependencies = [
        ('prosoponomikon', '0005_acquaintanceship_knows_as_description_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='acquaintanceship',
            options={'ordering': [rpg_project.utils.OrderByPolish('known_character__fullname')]},
        ),
        migrations.AlterModelOptions(
            name='acquisition',
            options={'ordering': [rpg_project.utils.OrderByPolish('character__fullname'), rpg_project.utils.OrderByPolish('skill_level__skill__name'), 'skill_level__level']},
        ),
        migrations.AlterModelOptions(
            name='character',
            options={'ordering': [rpg_project.utils.OrderByPolish('fullname')], 'verbose_name': '*Character', 'verbose_name_plural': '*Characters (ALL)'},
        ),
    ]
