# Generated by Django 3.2.8 on 2022-01-29 17:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rules', '0028_auto_20220129_1158'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='perk',
            name='modifiers_old',
        ),
    ]
