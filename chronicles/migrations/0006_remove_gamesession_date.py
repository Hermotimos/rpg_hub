# Generated by Django 4.1.7 on 2023-05-31 20:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chronicles', '0005_gamesession_dates_gamesession_duration_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gamesession',
            name='date',
        ),
    ]
