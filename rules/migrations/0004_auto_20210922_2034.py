# Generated by Django 3.1 on 2021-09-22 18:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rules', '0003_auto_20210922_1956'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='plate',
            name='pictures',
        ),
        migrations.RemoveField(
            model_name='shield',
            name='pictures',
        ),
        migrations.RemoveField(
            model_name='weapon',
            name='pictures',
        ),
    ]