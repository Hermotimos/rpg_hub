# Generated by Django 3.2.8 on 2022-01-19 22:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rules', '0012_auto_20220119_2218'),
    ]

    operations = [
        migrations.AlterField(
            model_name='factor',
            name='name',
            field=models.CharField(max_length=30, unique=True),
        ),
    ]
