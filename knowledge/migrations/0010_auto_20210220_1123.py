# Generated by Django 3.1 on 2021-02-20 10:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('knowledge', '0009_auto_20210220_1118'),
    ]

    operations = [
        migrations.AlterField(
            model_name='biographypacket',
            name='order_no',
            field=models.SmallIntegerField(default=1, verbose_name='Nr porządkowy'),
        ),
    ]
