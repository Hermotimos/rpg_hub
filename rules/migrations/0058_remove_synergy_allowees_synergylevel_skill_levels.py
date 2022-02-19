# Generated by Django 4.0.2 on 2022-02-18 15:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rules', '0057_alter_conditionalmodifier_options_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='synergy',
            name='allowees',
        ),
        migrations.AddField(
            model_name='synergylevel',
            name='skill_levels',
            field=models.ManyToManyField(related_name='synergy_levels', to='rules.SkillLevel'),
        ),
    ]