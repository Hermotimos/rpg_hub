# Generated by Django 3.1 on 2021-03-05 12:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prosoponomikon', '0038_auto_20210227_0001'),
    ]

    operations = [
        migrations.AlterField(
            model_name='character',
            name='name',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
