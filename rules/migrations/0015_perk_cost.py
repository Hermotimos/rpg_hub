# Generated by Django 3.2.8 on 2022-01-22 10:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rules', '0014_alter_factor_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='perk',
            name='cost',
            field=models.TextField(blank=True, max_length=1000, null=True),
        ),
    ]