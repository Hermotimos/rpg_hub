# Generated by Django 3.1 on 2020-12-25 19:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prosoponomikon', '0003_auto_20201225_2018'),
    ]

    operations = [
        migrations.AddField(
            model_name='character',
            name='descr_psychophysical',
            field=models.TextField(blank=True, null=True),
        ),
    ]
