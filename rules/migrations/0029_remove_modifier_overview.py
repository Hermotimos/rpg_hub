# Generated by Django 4.0.4 on 2022-07-09 14:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rules', '0028_alter_damagetype_unique_together_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='modifier',
            name='overview',
        ),
    ]
