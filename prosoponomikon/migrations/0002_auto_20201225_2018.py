# Generated by Django 3.1 on 2020-12-25 19:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prosoponomikon', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='character',
            name='description_short',
            field=models.TextField(blank=True, null=True),
        ),
    ]
