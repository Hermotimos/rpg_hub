# Generated by Django 3.1 on 2021-02-21 14:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prosoponomikon', '0024_character_cognomen'),
    ]

    operations = [
        migrations.AlterField(
            model_name='character',
            name='cognomen',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]
