# Generated by Django 4.0.2 on 2022-03-25 11:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial_squashed'),
        ('toponomikon', '0006_rename_known_indirectly_location_informees'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='informees',
            field=models.ManyToManyField(blank=True, limit_choices_to=models.Q(('status', 'player')), related_name='locations_informed', to='users.Profile'),
        ),
    ]
