# Generated by Django 4.1.7 on 2023-05-21 14:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_profile_image_icons_color'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='image_icons_color',
        ),
    ]
