# Generated by Django 3.2.8 on 2022-01-17 18:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rules', '0003_auto_20220116_2236'),
    ]

    operations = [
        migrations.CreateModel(
            name='Factor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=15, unique=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Modifier',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.SmallIntegerField()),
                ('condition', models.CharField(blank=True, max_length=200, null=True, unique=True)),
                ('factor', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='modifiers', to='rules.factor')),
            ],
            options={
                'ordering': ['value', 'factor', 'condition'],
            },
        ),
        migrations.CreateModel(
            name='Perk',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=50, null=True, unique=True)),
                ('description', models.TextField(blank=True, max_length=4000, null=True)),
                ('modifiers', models.ManyToManyField(blank=True, related_name='perks', to='rules.Modifier')),
            ],
            options={
                'ordering': ['name', 'description'],
            },
        ),
        migrations.AddField(
            model_name='skilllevel',
            name='perks',
            field=models.ManyToManyField(blank=True, related_name='skill_levels', to='rules.Perk'),
        ),
        migrations.AddField(
            model_name='synergylevel',
            name='perks',
            field=models.ManyToManyField(blank=True, related_name='synergy_levels', to='rules.Perk'),
        ),
    ]
