# Generated by Django 3.1 on 2020-09-26 09:22

from django.db import migrations


class Migration(migrations.Migration):
    atomic = False
    
    dependencies = [
        ('rules', '0004_auto_20200926_1117'),
    ]

    operations = [
        migrations.RenameModel('ShieldType', 'Shield')
    ]