# Generated by Django 3.1 on 2020-09-26 16:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('development', '0004_auto_20200926_1831'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='level',
            name='experience',
        ),
        migrations.AddField(
            model_name='profileklass',
            name='experience',
            field=models.PositiveSmallIntegerField(default=1),
            preserve_default=False,
        ),
    ]