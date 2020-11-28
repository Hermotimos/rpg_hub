# Generated by Django 3.1 on 2020-11-11 11:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
        ('chronicles', '0016_remove_timeunit_debate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timeunit',
            name='known_directly',
            field=models.ManyToManyField(blank=True, limit_choices_to=models.Q(status__in=['active_player', 'inactive_player', 'dead_player']), related_name='events_known_directly', to='users.Profile'),
        ),
        migrations.AlterField(
            model_name='timeunit',
            name='known_indirectly',
            field=models.ManyToManyField(blank=True, limit_choices_to=models.Q(status__in=['active_player', 'inactive_player', 'dead_player']), related_name='events_known_indirectly', to='users.Profile'),
        ),
        migrations.AlterField(
            model_name='timeunit',
            name='known_long_desc',
            field=models.ManyToManyField(blank=True, limit_choices_to=models.Q(status__in=['active_player', 'inactive_player', 'dead_player']), related_name='timeunits_long_desc', to='users.Profile'),
        ),
        migrations.AlterField(
            model_name='timeunit',
            name='known_short_desc',
            field=models.ManyToManyField(blank=True, limit_choices_to=models.Q(status__in=['active_player', 'inactive_player', 'dead_player']), related_name='timeunits_known_short_desc', to='users.Profile'),
        ),
    ]
