# Generated by Django 3.2.8 on 2022-01-30 06:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rules', '0030_auto_20220129_2212'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shield',
            name='armor_class_bonus_close_combat',
        ),
        migrations.RemoveField(
            model_name='shield',
            name='armor_class_bonus_distance_combat',
        ),
        migrations.RemoveField(
            model_name='shield',
            name='enemies_no',
        ),
        migrations.AddField(
            model_name='shield',
            name='armor_class_bonus',
            field=models.PositiveSmallIntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='shield',
            name='comment',
            field=models.TextField(blank=True, max_length=200, null=True),
        ),
    ]
