# Generated by Django 3.2.8 on 2022-01-29 10:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rules', '0027_alter_condition_text'),
    ]

    operations = [
        migrations.AlterField(
            model_name='combattype',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='condition',
            name='text',
            field=models.CharField(max_length=200, unique=True),
        ),
    ]
