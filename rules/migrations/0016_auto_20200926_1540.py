# Generated by Django 3.1 on 2020-09-26 13:40

from django.db import migrations


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('users', '0002_auto_20200926_1248'),
        ('rules', '0015_auto_20200926_1538'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='EliteClass',
            new_name='EliteProfession',
        ),
    ]