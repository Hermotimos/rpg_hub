# Generated by Django 3.1 on 2020-09-26 09:28

from django.db import migrations


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('rules', '0006_auto_20200926_1125'),
    ]

    operations = [
        migrations.RenameModel('WeaponType', 'Weapon')
    ]