# Generated by Django 3.1 on 2020-09-26 13:25

from django.db import migrations


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('rules', '0010_auto_20200926_1524'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='CharacterClass',
            new_name='Profession',
        ),
    ]
