# Generated by Django 3.1 on 2021-02-26 23:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prosoponomikon', '0037_auto_20210226_1740'),
    ]

    operations = [
        migrations.RenameField(
            model_name='namegroup',
            old_name='title',
            new_name='name',
        ),
        migrations.AlterField(
            model_name='nameform',
            name='form',
            field=models.CharField(max_length=250, unique=True),
        ),
    ]
