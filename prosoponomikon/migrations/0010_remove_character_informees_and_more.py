# Generated by Django 4.0.4 on 2022-06-22 18:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('prosoponomikon', '0009_alter_acquaintanceship_options_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='character',
            name='informees',
        ),
        migrations.RemoveField(
            model_name='character',
            name='participants',
        ),
    ]
