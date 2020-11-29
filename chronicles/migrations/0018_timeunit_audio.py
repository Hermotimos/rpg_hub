# Generated by Django 3.1 on 2020-11-11 18:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('imaginarion', '0001_initial'),
        ('chronicles', '0017_auto_20201111_1223'),
    ]

    operations = [
        migrations.AddField(
            model_name='timeunit',
            name='audio',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='events', to='imaginarion.audio'),
        ),
    ]
