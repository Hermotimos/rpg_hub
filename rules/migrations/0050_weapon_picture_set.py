# Generated by Django 4.0.2 on 2022-02-14 17:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('imaginarion', '0012_pictureset'),
        ('rules', '0049_rename_allowed_profiles_eliteklass_allowees_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='weapon',
            name='picture_set',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='imaginarion.pictureset'),
        ),
    ]