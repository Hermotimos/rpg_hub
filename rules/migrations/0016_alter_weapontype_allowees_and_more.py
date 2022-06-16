# Generated by Django 4.0.4 on 2022-06-15 16:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_remove_profile_character_name_copy'),
        ('rules', '0015_damagetype_range_alter_damagetype_special'),
    ]

    operations = [
        migrations.AlterField(
            model_name='weapontype',
            name='allowees',
            field=models.ManyToManyField(blank=True, limit_choices_to=models.Q(('status', 'player')), related_name='allowed_weapon_types', to='users.profile'),
        ),
        migrations.AlterUniqueTogether(
            name='damagetype',
            unique_together={('description', 'type', 'damage', 'special', 'range')},
        ),
    ]