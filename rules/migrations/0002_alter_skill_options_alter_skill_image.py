# Generated by Django 4.0.4 on 2022-05-19 03:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rules', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='skill',
            options={'ordering': ['name']},
        ),
        migrations.AlterField(
            model_name='skill',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='skills'),
        ),
    ]
