# Generated by Django 2.2.1 on 2020-07-05 13:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chronicles', '0006_auto_20200705_1436'),
    ]

    operations = [
        migrations.AddField(
            model_name='timeunit',
            name='dates',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
