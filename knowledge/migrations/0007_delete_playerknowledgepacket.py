# Generated by Django 3.1 on 2020-11-08 21:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('toponomikon', '0001_initial'),
        ('knowledge', '0006_playerknowledgepacket'),
    ]

    operations = [
        migrations.DeleteModel(
            name='PlayerKnowledgePacket',
        ),
    ]
