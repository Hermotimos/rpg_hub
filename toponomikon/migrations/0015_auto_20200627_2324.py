# Generated by Django 2.2.1 on 2020-06-27 21:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('toponomikon', '0014_secondarylocation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='locationtype',
            name='order_no',
            field=models.PositiveSmallIntegerField(default=1),
            preserve_default=False,
        ),
    ]