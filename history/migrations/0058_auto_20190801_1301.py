# Generated by Django 2.2.1 on 2019-08-01 11:01

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0057_auto_20190801_1228'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='year',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(1)]),
        ),
    ]
