# Generated by Django 4.0.2 on 2022-02-20 09:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rules', '0058_remove_synergy_allowees_synergylevel_skill_levels'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='conditionalmodifier',
            options={'ordering': ['modifier']},
        ),
    ]
