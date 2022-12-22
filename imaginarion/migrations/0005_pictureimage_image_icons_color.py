# Generated by Django 4.0.4 on 2022-12-22 16:50

from django.db import migrations
import rpg_project.utils


class Migration(migrations.Migration):

    dependencies = [
        ('imaginarion', '0004_alter_pictureimage_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='pictureimage',
            name='image_icons_color',
            field=rpg_project.utils.ColorSchemeChoiceField(choices=[('light', 'light'), ('dark', 'dark'), ('info', 'info'), ('warning', 'warning'), ('danger', 'danger')], default='light', max_length=9),
        ),
    ]