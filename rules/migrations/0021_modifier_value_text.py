# Generated by Django 3.2.8 on 2022-01-26 19:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rules', '0020_alter_modifier_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='modifier',
            name='value_text',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]