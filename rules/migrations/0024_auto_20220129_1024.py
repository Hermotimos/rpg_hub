# Generated by Django 3.2.8 on 2022-01-29 09:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rules', '0023_rename_modifiers_perk_modifiers_old'),
    ]

    operations = [
        migrations.CreateModel(
            name='CombatType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(max_length=100)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Condition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(max_length=4000)),
            ],
            options={
                'ordering': ['text'],
            },
        ),
        migrations.CreateModel(
            name='ConditionalModifier',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('combat_types', models.ManyToManyField(blank=True, related_name='conditional_modifiers', to='rules.CombatType')),
                ('conditions', models.ManyToManyField(blank=True, related_name='conditional_modifiers', to='rules.Condition')),
                ('modifier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rules.modifier')),
                ('perk', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rules.perk')),
            ],
            options={
                'ordering': ['modifier'],
            },
        ),
        migrations.AddField(
            model_name='perk',
            name='modifiers',
            field=models.ManyToManyField(blank=True, related_name='perks_new', through='rules.ConditionalModifier', to='rules.Modifier'),
        ),
    ]
