# Generated by Django 4.0.4 on 2022-08-14 16:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rules', '0002_remove_skill_version_of'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='skilllevel',
            name='acquired_by',
        ),
        migrations.RemoveField(
            model_name='synergylevel',
            name='acquired_by',
        ),
    ]
