# Generated by Django 2.2.1 on 2020-07-05 12:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('toponomikon', '0016_tertiarylocation'),
        ('chronicles', '0005_timeunit_tertiary_locations'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='timeunit',
            name='primary_locations',
        ),
        migrations.RemoveField(
            model_name='timeunit',
            name='secondary_locations',
        ),
        migrations.RemoveField(
            model_name='timeunit',
            name='tertiary_locations',
        ),
        migrations.AddField(
            model_name='timeunit',
            name='locations',
            field=models.ManyToManyField(blank=True, related_name='events', to='toponomikon.Location'),
        ),
    ]