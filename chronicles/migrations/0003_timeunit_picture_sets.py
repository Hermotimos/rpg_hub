# Generated by Django 3.1 on 2021-03-12 11:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('imaginarion', '0012_pictureset'),
        ('chronicles', '0002_auto_20210106_1613'),
    ]

    operations = [
        migrations.AddField(
            model_name='timeunit',
            name='picture_sets',
            field=models.ManyToManyField(blank=True, related_name='events', to='imaginarion.PictureSet'),
        ),
    ]
