# Generated by Django 2.2.1 on 2020-07-09 19:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chronicles', '0009_auto_20200709_2127'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timeunit',
            name='game',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='game_events', to='chronicles.GameSession'),
        ),
        migrations.AlterField(
            model_name='timeunit',
            name='locations',
            field=models.ManyToManyField(blank=True, related_name='events', to='toponomikon.Location'),
        ),
    ]