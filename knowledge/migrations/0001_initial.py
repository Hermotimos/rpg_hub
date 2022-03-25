# Generated by Django 3.1 on 2020-11-29 08:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('imaginarion', '0001_initial'),
        ('users', '0001_initial'),
        ('rules', '0001_squashed_0005_auto_20211017_1835'),
    ]

    operations = [
        migrations.CreateModel(
            name='KnowledgePacket',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, unique=True)),
                ('text', models.TextField()),
                ('sorting_name', models.CharField(blank=True, max_length=250, null=True)),
                ('acquired_by', models.ManyToManyField(blank=True, related_name='knowledge_packets', to='users.Profile')),
                ('pictures', models.ManyToManyField(blank=True, related_name='knowledge_packets', to='imaginarion.Picture')),
                ('skills', models.ManyToManyField(related_name='knowledge_packets', to='rules.Skill')),
                ('author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='authored_kn_packets', to='users.profile')),
            ],
            options={
                'ordering': ['sorting_name'],
            },
        ),
        migrations.CreateModel(
            name='MapPacket',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, unique=True)),
                ('sorting_name', models.CharField(blank=True, max_length=250, null=True)),
                ('acquired_by', models.ManyToManyField(blank=True, related_name='map_packets', to='users.Profile')),
                ('pictures', models.ManyToManyField(related_name='map_packets', to='imaginarion.Picture')),
            ],
            options={
                'ordering': ['sorting_name'],
            },
        ),
    ]
