# Generated by Django 4.0.4 on 2022-08-07 09:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prosoponomikon', '0004_characteracquisitions_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='acquaintanceship',
            name='knows_as_description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='acquaintanceship',
            name='knows_as_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
