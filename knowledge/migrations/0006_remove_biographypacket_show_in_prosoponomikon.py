# Generated by Django 3.1 on 2021-01-17 15:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('knowledge', '0005_biographypacket_show_in_prosoponomikon'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='biographypacket',
            name='show_in_prosoponomikon',
        ),
    ]
