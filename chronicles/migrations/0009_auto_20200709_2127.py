# Generated by Django 2.2.1 on 2020-07-09 19:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
        ('chronicles', '0008_auto_20200707_0532'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='chapter',
            options={'ordering': ['chapter_no'], 'verbose_name': 'I. Chapter'},
        ),
        migrations.AlterModelOptions(
            name='gameevent',
            options={'ordering': ['game', 'event_no_in_game'], 'verbose_name': 'III. Game event'},
        ),
        migrations.AlterModelOptions(
            name='gamesession',
            options={'ordering': ['game_no'], 'verbose_name': 'II. Game session'},
        ),
        migrations.AlterModelOptions(
            name='timeunit',
            options={'ordering': ['date_start'], 'verbose_name_plural': '* Time Units (Time spans, History events, Game events)'},
        ),
        migrations.RemoveField(
            model_name='timeunit',
            name='year_end_ab_urbe_condita',
        ),
        migrations.RemoveField(
            model_name='timeunit',
            name='year_start_ab_urbe_condita',
        ),
        migrations.AddField(
            model_name='date',
            name='year_ab_urbe_condita',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='timeunit',
            name='known_long_desc',
            field=models.ManyToManyField(blank=True, limit_choices_to=models.Q(('status', 'active_player'), ('status', 'inactive_player'), ('status', 'dead_player'), _connector='OR'), related_name='timeunits_long_desc', to='users.Profile'),
        ),
        migrations.AddField(
            model_name='timeunit',
            name='known_short_desc',
            field=models.ManyToManyField(blank=True, limit_choices_to=models.Q(('status', 'active_player'), ('status', 'inactive_player'), ('status', 'dead_player'), _connector='OR'), related_name='timeunits_known_short_desc', to='users.Profile'),
        ),
        migrations.AlterField(
            model_name='date',
            name='season',
            field=models.CharField(blank=True, choices=[('1', 'Wiosna'), ('2', 'Lato'), ('3', 'Jesień'), ('4', 'Zima')], max_length=6, null=True),
        ),
        migrations.AlterField(
            model_name='timeunit',
            name='debate',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='event', to='debates.Debate'),
        ),
        migrations.AlterField(
            model_name='timeunit',
            name='game',
            field=models.ForeignKey(default=35, on_delete=django.db.models.deletion.PROTECT, related_name='game_events', to='chronicles.GameSession'),
        ),
        migrations.AlterField(
            model_name='timeunit',
            name='locations',
            field=models.ManyToManyField(related_name='events', to='toponomikon.Location'),
        ),
        migrations.AlterField(
            model_name='timeunit',
            name='pictures',
            field=models.ManyToManyField(blank=True, related_name='events', to='imaginarion.Picture'),
        ),
    ]