# Generated by Django 3.2.8 on 2022-01-31 18:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rules', '0034_auto_20220131_1911'),
    ]

    operations = [
        migrations.RenameField(
            model_name='plate',
            old_name='mod_hiding_wilderness',
            new_name='mod_hiding',
        ),
        migrations.RenameField(
            model_name='plate',
            old_name='mod_sneaking_wilderness',
            new_name='mod_sneaking',
        ),
    ]