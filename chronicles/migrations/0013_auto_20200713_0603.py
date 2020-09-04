# Generated by Django 2.2.1 on 2020-07-13 04:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chronicles', '0012_auto_20200712_1917'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('chronicles.timeunit',),
        ),
        migrations.AlterField(
            model_name='timeunit',
            name='date_end',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='timeunits_ended', to='chronicles.Date', verbose_name='Date end (year of the encompassing unit)'),
        ),
        migrations.AlterField(
            model_name='timeunit',
            name='date_start',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='timeunits_started', to='chronicles.Date', verbose_name='Date start (year of the encompassing unit)'),
        ),
        migrations.AlterField(
            model_name='timeunit',
            name='in_timeunit',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='timeunits', to='chronicles.TimeUnit'),
        ),
    ]
