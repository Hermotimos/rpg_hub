# Generated by Django 3.1 on 2021-08-01 15:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prosoponomikon', '0062_auto_20210320_1809'),
    ]

    operations = [
        migrations.AddField(
            model_name='familyname',
            name='info',
            field=models.TextField(blank=True, null=True),
        ),
    ]
