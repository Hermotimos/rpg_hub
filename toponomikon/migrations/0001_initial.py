# Generated by Django 2.2.1 on 2020-03-25 17:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('imaginarion', '0001_initial'),
        ('users', '0001_initial'),
        ('knowledge', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GeneralLocation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, max_length=4000, null=True)),
                ('sorting_name', models.CharField(blank=True, max_length=250, null=True, unique=True)),
                ('knowledge_packets', models.ManyToManyField(blank=True, related_name='general_locations', to='knowledge.KnowledgePacket')),
                ('known_directly', models.ManyToManyField(blank=True, limit_choices_to=models.Q(('status', 'active_player'), ('status', 'inactive_player'), ('status', 'dead_player'), _connector='OR'), related_name='gen_locs_known_directly', to='users.Profile')),
                ('known_indirectly', models.ManyToManyField(blank=True, limit_choices_to=models.Q(('status', 'active_player'), ('status', 'inactive_player'), ('status', 'dead_player'), _connector='OR'), related_name='gen_locs_known_indirectly', to='users.Profile')),
            ],
            options={
                'ordering': ['sorting_name'],
            },
        ),
        migrations.CreateModel(
            name='LocationType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('default_img', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='location_types', to='imaginarion.Picture')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='SpecificLocation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, max_length=4000, null=True)),
                ('sorting_name', models.CharField(blank=True, max_length=250, null=True, unique=True)),
                ('general_location', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='specific_locations', to='toponomikon.GeneralLocation')),
                ('knowledge_packets', models.ManyToManyField(blank=True, related_name='specific_locations', to='knowledge.KnowledgePacket')),
                ('known_directly', models.ManyToManyField(blank=True, limit_choices_to=models.Q(('status', 'active_player'), ('status', 'inactive_player'), ('status', 'dead_player'), _connector='OR'), related_name='spec_locs_known_directly', to='users.Profile')),
                ('known_indirectly', models.ManyToManyField(blank=True, limit_choices_to=models.Q(('status', 'active_player'), ('status', 'inactive_player'), ('status', 'dead_player'), _connector='OR'), related_name='spec_locs_known_indirectly', to='users.Profile')),
                ('location_type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='specific_locations', to='toponomikon.LocationType')),
                ('main_image', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='spec_loc_main_pics', to='imaginarion.Picture')),
                ('pictures', models.ManyToManyField(blank=True, related_name='spec_loc_pics', to='imaginarion.Picture')),
            ],
            options={
                'ordering': ['sorting_name'],
            },
        ),
        migrations.AddField(
            model_name='generallocation',
            name='location_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='general_locations', to='toponomikon.LocationType'),
        ),
        migrations.AddField(
            model_name='generallocation',
            name='main_image',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='gen_loc_main_pics', to='imaginarion.Picture'),
        ),
        migrations.AddField(
            model_name='generallocation',
            name='pictures',
            field=models.ManyToManyField(blank=True, related_name='gen_loc_pics', to='imaginarion.Picture'),
        ),
    ]
