# Generated by Django 3.1 on 2020-09-26 13:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20200926_1248'),
        ('rules', '0013_auto_20200926_1536'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eliteprofession',
            name='allowed_profiles',
            field=models.ManyToManyField(blank=True, limit_choices_to=models.Q(('status', 'active_player'), ('status', 'inactive_player'), ('status', 'dead_player'), _connector='OR'), related_name='allowed_elite_klasses', to='users.Profile'),
        ),
        migrations.AlterField(
            model_name='eliteprofession',
            name='elite_profession',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='elite_klasses', to='rules.eliteclass'),
        ),
    ]
