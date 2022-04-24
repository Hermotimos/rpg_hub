# Generated by Django 4.0.2 on 2022-04-24 20:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rules', '0006_remove_subprofession_starting_skills_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subprofession',
            name='developed_skilllevels',
        ),
        migrations.RemoveField(
            model_name='subprofession',
            name='starting_skilllevels',
        ),
        migrations.AddField(
            model_name='subprofession',
            name='essential_skills',
            field=models.ManyToManyField(blank=True, to='rules.Skill'),
        ),
    ]
