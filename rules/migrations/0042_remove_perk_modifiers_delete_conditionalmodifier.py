# Generated by Django 4.0.2 on 2022-02-13 14:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rules', '0041_bonus_perk_bonuses'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='perk',
            name='modifiers',
        ),
        migrations.DeleteModel(
            name='ConditionalModifier',
        ),
    ]
