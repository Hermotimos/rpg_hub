# Generated by Django 2.2.1 on 2020-07-07 03:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('debates', '0005_auto_20200707_0505'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='debate',
            name='allowed_profiles',
        ),
    ]
