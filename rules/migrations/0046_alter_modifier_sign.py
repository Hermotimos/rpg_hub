# Generated by Django 4.0.2 on 2022-02-14 14:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rules', '0045_conditionalmodifier_overview_modifier_overview'),
    ]

    operations = [
        migrations.AlterField(
            model_name='modifier',
            name='sign',
            field=models.CharField(blank=True, choices=[('-', '-'), ('+', '+')], default='+', max_length=5, null=True),
        ),
    ]
