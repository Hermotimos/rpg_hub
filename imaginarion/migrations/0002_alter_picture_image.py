# Generated by Django 4.0.4 on 2022-05-06 08:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('imaginarion', '0001_initial_squashed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='picture',
            name='image',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pictures', to='imaginarion.pictureimage'),
        ),
    ]
