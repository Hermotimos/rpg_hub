# Generated by Django 3.1 on 2021-09-22 15:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('knowledge', '0014_knowledgepacket_picture_sets'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='knowledgepacket',
            name='pictures',
        ),
    ]