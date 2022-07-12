# Generated by Django 4.0.4 on 2022-07-12 11:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rules', '0001_initial'),
        ('prosoponomikon', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Acquisition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'ordering': ['character', 'skill_level__skill'],
            },
        ),
        migrations.AddField(
            model_name='character',
            name='skill_levels',
            field=models.ManyToManyField(blank=True, related_name='acquiring_characters', through='prosoponomikon.Acquisition', to='rules.skilllevel'),
        ),
        migrations.AddField(
            model_name='acquisition',
            name='character',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='prosoponomikon.character'),
        ),
        migrations.AddField(
            model_name='acquisition',
            name='skill_level',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rules.skilllevel'),
        ),
        migrations.AddField(
            model_name='acquisition',
            name='sphragis',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='rules.sphragis'),
        ),
        migrations.AddField(
            model_name='acquisition',
            name='weapon',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='rules.weapontype'),
        ),
        migrations.AlterUniqueTogether(
            name='acquisition',
            unique_together={('character', 'skill_level')},
        ),
    ]