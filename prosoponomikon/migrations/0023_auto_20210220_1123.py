# Generated by Django 3.1 on 2021-02-20 10:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prosoponomikon', '0022_auto_20210131_1902'),
    ]

    operations = [
        migrations.AlterField(
            model_name='charactergroup',
            name='order_no',
            field=models.SmallIntegerField(default=1, verbose_name='Nr porządkowy'),
        ),
    ]
