# Generated by Django 4.0.2 on 2022-04-18 17:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('toponomikon', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='location',
            options={'ordering': ['sorting_name'], 'verbose_name': 'Location', 'verbose_name_plural': '--- LOCATIONS'},
        ),
    ]
