# Generated by Django 3.1 on 2021-01-21 18:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('imaginarion', '0002_auto_20210103_1049'),
    ]

    operations = [
        migrations.AlterField(
            model_name='audio',
            name='type',
            field=models.CharField(choices=[('domeny', 'DOMENY'), ('npc', 'NPC'), ('topoi', 'TOPOI'), ('varia', 'VARIA')], max_length=10),
        ),
    ]