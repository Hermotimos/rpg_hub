# Generated by Django 4.0.4 on 2022-05-23 15:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('toponomikon', '0002_alter_location_options_remove_location_sorting_name'),
        ('prosoponomikon', '0003_alter_character_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='character',
            name='cognomen',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='character',
            name='frequented_locations',
            field=models.ManyToManyField(blank=True, related_name='characters', to='toponomikon.location'),
        ),
        migrations.AlterField(
            model_name='character',
            name='fullname',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='familyname',
            name='form',
            field=models.CharField(max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name='firstname',
            name='form',
            field=models.CharField(max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name='firstname',
            name='form_2',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
