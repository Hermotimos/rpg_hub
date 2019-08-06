# Generated by Django 2.2.1 on 2019-07-12 22:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20190712_0822'),
        ('history', '0004_eventdescription'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventDescribed',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(max_length=4000)),
                ('game_no', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='events_described', to='history.GameSession')),
                ('informed', models.ManyToManyField(blank=True, limit_choices_to={'character_status': 'player'}, related_name='events_described_informed', to='users.Profile')),
                ('participants', models.ManyToManyField(blank=True, limit_choices_to={'character_status': 'player'}, related_name='events_described_participated', to='users.Profile')),
            ],
        ),
        migrations.DeleteModel(
            name='EventDescription',
        ),
    ]
