# Generated by Django 4.0.4 on 2022-07-09 17:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rules', '0030_remove_conditionalmodifier_overview'),
    ]

    operations = [
        migrations.AlterField(
            model_name='skilllevel',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
