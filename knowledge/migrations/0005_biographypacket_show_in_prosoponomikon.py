# Generated by Django 3.1 on 2021-01-03 07:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('knowledge', '0004_auto_20201228_2101'),
    ]

    operations = [
        migrations.AddField(
            model_name='biographypacket',
            name='show_in_prosoponomikon',
            field=models.BooleanField(blank=True, null=True),
        ),
    ]
