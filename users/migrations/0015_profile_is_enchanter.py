# Generated by Django 4.0.2 on 2022-02-19 07:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0014_alter_profile_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='is_enchanter',
            field=models.BooleanField(default=False),
        ),
    ]