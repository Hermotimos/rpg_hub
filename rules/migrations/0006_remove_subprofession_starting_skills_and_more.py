# Generated by Django 4.0.2 on 2022-04-24 19:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rules', '0005_delete_primaryprofession_delete_secondaryprofession_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subprofession',
            name='starting_skills',
        ),
        migrations.AddField(
            model_name='subprofession',
            name='developed_skilllevels',
            field=models.ManyToManyField(blank=True, related_name='y', to='rules.SkillLevel'),
        ),
        migrations.AddField(
            model_name='subprofession',
            name='starting_skilllevels',
            field=models.ManyToManyField(blank=True, related_name='x', to='rules.SkillLevel'),
        ),
    ]
