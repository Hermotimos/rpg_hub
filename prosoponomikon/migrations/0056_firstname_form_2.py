# Generated by Django 3.1 on 2021-03-19 08:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prosoponomikon', '0055_auto_20210318_2315'),
    ]

    operations = [
        migrations.AddField(
            model_name='firstname',
            name='form_2',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]
