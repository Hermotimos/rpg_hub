# Generated by Django 3.1 on 2021-10-17 13:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chronicles', '0006_plotthread'),
    ]

    operations = [
        migrations.AddField(
            model_name='timeunit',
            name='plot_threads',
            field=models.ManyToManyField(blank=True, related_name='events', to='chronicles.PlotThread'),
        ),
    ]