# Generated by Django 2.2.1 on 2020-04-05 15:22

from django.db import migrations, models
import rpg_project.utils


class Migration(migrations.Migration):

    dependencies = [
        ('imaginarion', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='picture',
            name='image',
            field=models.ImageField(storage=rpg_project.utils.ReplaceFileStorage(), upload_to='post_pics'),
        ),
    ]
