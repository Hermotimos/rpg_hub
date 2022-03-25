# Generated by Django 4.0.2 on 2022-03-25 11:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial_squashed'),
        ('prosoponomikon', '0004_rename_witnesses_character_participants'),
    ]

    operations = [
        migrations.AlterField(
            model_name='character',
            name='participants',
            field=models.ManyToManyField(blank=True, related_name='characters_participated', to='users.Profile'),
        ),
    ]
