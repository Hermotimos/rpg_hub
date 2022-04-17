# Generated by Django 4.0.2 on 2022-04-17 06:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rules', '0002_profession_allowees_alter_klass_allowees'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='klass',
            name='lvl_1',
        ),
        migrations.RemoveField(
            model_name='klass',
            name='lvl_10',
        ),
        migrations.RemoveField(
            model_name='klass',
            name='lvl_11',
        ),
        migrations.RemoveField(
            model_name='klass',
            name='lvl_12',
        ),
        migrations.RemoveField(
            model_name='klass',
            name='lvl_13',
        ),
        migrations.RemoveField(
            model_name='klass',
            name='lvl_14',
        ),
        migrations.RemoveField(
            model_name='klass',
            name='lvl_15',
        ),
        migrations.RemoveField(
            model_name='klass',
            name='lvl_16',
        ),
        migrations.RemoveField(
            model_name='klass',
            name='lvl_17',
        ),
        migrations.RemoveField(
            model_name='klass',
            name='lvl_18',
        ),
        migrations.RemoveField(
            model_name='klass',
            name='lvl_19',
        ),
        migrations.RemoveField(
            model_name='klass',
            name='lvl_2',
        ),
        migrations.RemoveField(
            model_name='klass',
            name='lvl_20',
        ),
        migrations.RemoveField(
            model_name='klass',
            name='lvl_3',
        ),
        migrations.RemoveField(
            model_name='klass',
            name='lvl_4',
        ),
        migrations.RemoveField(
            model_name='klass',
            name='lvl_5',
        ),
        migrations.RemoveField(
            model_name='klass',
            name='lvl_6',
        ),
        migrations.RemoveField(
            model_name='klass',
            name='lvl_7',
        ),
        migrations.RemoveField(
            model_name='klass',
            name='lvl_8',
        ),
        migrations.RemoveField(
            model_name='klass',
            name='lvl_9',
        ),
        migrations.AddField(
            model_name='profession',
            name='profession',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='professions', to='rules.profession'),
        ),
        migrations.AddField(
            model_name='profession',
            name='starting_skills',
            field=models.ManyToManyField(blank=True, to='rules.Skill'),
        ),
    ]
