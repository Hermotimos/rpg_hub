# Generated by Django 3.1 on 2021-10-15 15:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0010_auto_20211015_1350'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='news',
            name='seen_by',
        ),
    ]
