# Generated by Django 3.1 on 2021-10-20 15:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('communications', '0002_auto_20211020_1651'),
    ]

    operations = [
        migrations.AlterField(
            model_name='thread',
            name='is_exclusive',
            field=models.BooleanField(default=False),
        ),
    ]
