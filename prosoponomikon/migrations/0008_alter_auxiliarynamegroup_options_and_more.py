# Generated by Django 4.0.4 on 2022-08-28 07:48

from django.db import migrations
import rpg_project.utils


class Migration(migrations.Migration):

    dependencies = [
        ('prosoponomikon', '0007_character_created_by'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='auxiliarynamegroup',
            options={'ordering': [rpg_project.utils.OrderByPolish('social_info'), rpg_project.utils.OrderByPolish('location__name')]},
        ),
        migrations.AlterModelOptions(
            name='firstname',
            options={'ordering': [rpg_project.utils.OrderByPolish('auxiliary_group__social_info'), rpg_project.utils.OrderByPolish('auxiliary_group__location__name'), 'form']},
        ),
    ]