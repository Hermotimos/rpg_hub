# Generated by Django 3.1 on 2020-11-29 08:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('rules', '0001_initial'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Achievement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='achievements', to='users.profile')),
            ],
        ),
        migrations.CreateModel(
            name='ProfileKlass',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('klass', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='profile_klasses', to='rules.klass')),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='profile_klasses', to='users.profile')),
                ('experience', models.PositiveSmallIntegerField()),
                ('title', models.CharField(blank=True, max_length=200, null=True)),
            ],
            options={
                'verbose_name': 'Profile Klass',
                'verbose_name_plural': 'Profile Klasses',
                'ordering': ['profile__character_name'],
            },
        ),
        migrations.CreateModel(
            name='Level',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level_number', models.PositiveSmallIntegerField()),
                ('achievements', models.ManyToManyField(blank=True, related_name='levels', to='development.Achievement')),
                ('profile_klass', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='levels', to='development.profileklass')),
                ('level_mods', models.TextField()),
            ],
            options={
                'ordering': ['profile_klass', 'level_number'],
            },
        ),
    ]
