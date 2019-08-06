# Generated by Django 2.2.1 on 2019-07-24 10:42

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0031_auto_20190718_2119'),
    ]

    operations = [
        migrations.AddField(
            model_name='describedevent',
            name='event_no_in_game',
            field=models.PositiveSmallIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)]),
            preserve_default=False,
        ),
    ]
