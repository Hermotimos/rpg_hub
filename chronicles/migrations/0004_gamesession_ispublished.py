# Generated by Django 4.1.7 on 2023-03-11 17:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chronicles', '0003_alter_gamesession_options_gamesession_order_no'),
    ]

    operations = [
        migrations.AddField(
            model_name='gamesession',
            name='ispublished',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='gamesession',
            name='ispublished',
            field=models.BooleanField(default=False),
        ),
    ]
