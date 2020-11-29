# Generated by Django 3.1 on 2020-11-29 08:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('knowledge', '0001_initial'),
        ('users', '0001_initial'),
        # ('knowledge', '0001_initial'),
        # ('knowledge', '0004_mappacket'),
        ('imaginarion', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LocationType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('default_img', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='location_types', to='imaginarion.picture')),
                ('name_plural', models.CharField(blank=True, max_length=100, null=True)),
                ('order_no', models.PositiveSmallIntegerField()),
            ],
            options={
                'ordering': ['order_no'],
            },
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('sorting_name', models.CharField(blank=True, max_length=250, null=True)),
                ('in_location', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='locations', to='toponomikon.location')),
                ('knowledge_packets', models.ManyToManyField(blank=True, related_name='locations', to='knowledge.KnowledgePacket')),
                ('known_directly', models.ManyToManyField(blank=True, limit_choices_to=models.Q(status__in=['active_player', 'inactive_player', 'dead_player']), related_name='locs_known_directly', to='users.Profile')),
                ('known_indirectly', models.ManyToManyField(blank=True, limit_choices_to=models.Q(status__in=['active_player', 'inactive_player', 'dead_player']), related_name='locs_known_indirectly', to='users.Profile')),
                ('location_type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='locations', to='toponomikon.locationtype')),
                ('main_image', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='locations_main_pics', to='imaginarion.picture')),
                ('pictures', models.ManyToManyField(blank=True, related_name='locations_pics', to='imaginarion.Picture')),
                ('map_packets', models.ManyToManyField(blank=True, related_name='locations', to='knowledge.MapPacket')),
                ('audio_set', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='locations', to='imaginarion.audioset')),
            ],
            options={
                'ordering': ['sorting_name'],
            },
        ),
        migrations.CreateModel(
            name='MainLocation',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('toponomikon.location',),
        ),
        migrations.DeleteModel(
            name='MainLocation',
        ),
        migrations.CreateModel(
            name='PrimaryLocation',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('toponomikon.location',),
        ),
        migrations.CreateModel(
            name='SecondaryLocation',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('toponomikon.location',),
        ),
        migrations.CreateModel(
            name='TertiaryLocation',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('toponomikon.location',),
        ),
        migrations.DeleteModel(
            name='TertiaryLocation',
        ),
    ]
