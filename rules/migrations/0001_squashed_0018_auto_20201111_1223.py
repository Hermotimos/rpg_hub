# Generated by Django 3.1 on 2020-11-28 19:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    replaces = [('rules', '0001_initial'), ('rules', '0002_auto_20200721_2309'), ('rules', '0003_historyskill'), ('rules', '0004_auto_20200926_1117'), ('rules', '0005_auto_20200926_1122'), ('rules', '0006_auto_20200926_1125'), ('rules', '0007_auto_20200926_1128'), ('rules', '0008_auto_20200926_1129'), ('rules', '0009_auto_20200926_1143'), ('rules', '0010_auto_20200926_1524'), ('rules', '0011_auto_20200926_1525'), ('rules', '0012_auto_20200926_1527'), ('rules', '0013_auto_20200926_1536'), ('rules', '0014_auto_20200926_1538'), ('rules', '0015_auto_20200926_1538'), ('rules', '0016_auto_20200926_1540'), ('rules', '0017_auto_20200926_1738'), ('rules', '0018_auto_20201111_1223')]

    initial = True

    dependencies = [
        ('imaginarion', '0001_initial'),
        ('users', '0001_initial'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Skill',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Umiejętność')),
                ('tested_trait', models.CharField(blank=True, max_length=50, null=True, verbose_name='Cecha/Cechy')),
                ('image', models.ImageField(blank=True, null=True, upload_to='site_features_pics')),
                ('sorting_name', models.CharField(blank=True, max_length=101, null=True)),
                ('allowed_profiles', models.ManyToManyField(blank=True, limit_choices_to=models.Q(status__in=['active_player', 'inactive_player', 'dead_player']), related_name='allowed_skills', to='users.Profile')),
            ],
            options={
                'ordering': ['sorting_name'],
            },
        ),
        migrations.CreateModel(
            name='Synergy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Synergia')),
                ('sorting_name', models.CharField(blank=True, max_length=250, null=True)),
                ('allowed_profiles', models.ManyToManyField(blank=True, limit_choices_to=models.Q(status__in=['active_player', 'inactive_player', 'dead_player']), related_name='allowed_synergies', to='users.Profile')),
                ('skills', models.ManyToManyField(related_name='skills', to='rules.Skill')),
            ],
            options={
                'verbose_name': 'synergy',
                'verbose_name_plural': 'synergies',
                'ordering': ['sorting_name'],
            },
        ),
        migrations.CreateModel(
            name='SynergyLevel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.CharField(choices=[('1', '1'), ('2', '2'), ('3', '3')], max_length=10)),
                ('description', models.TextField(blank=True, max_length=4000, null=True)),
                ('sorting_name', models.CharField(blank=True, max_length=250, null=True)),
                ('acquired_by', models.ManyToManyField(blank=True, related_name='synergy_levels', to='users.Profile')),
                ('synergy', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='synergy_levels', to='rules.synergy')),
            ],
            options={
                'ordering': ['sorting_name'],
            },
        ),
        migrations.CreateModel(
            name='SkillLevel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.CharField(choices=[('0', '0'), ('1', '1'), ('2', '2'), ('3', '3')], max_length=10)),
                ('description', models.TextField(blank=True, max_length=4000, null=True)),
                ('sorting_name', models.CharField(blank=True, max_length=250, null=True)),
                ('acquired_by', models.ManyToManyField(blank=True, related_name='skill_levels', to='users.Profile')),
                ('skill', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='skill_levels', to='rules.skill')),
            ],
            options={
                'ordering': ['sorting_name'],
            },
        ),
        migrations.CreateModel(
            name='BooksSkill',
            fields=[
            ],
            options={
                'verbose_name': 'Księgi',
                'verbose_name_plural': 'Skills - BOOKS',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('rules.skill',),
        ),
        migrations.CreateModel(
            name='TheologySkill',
            fields=[
            ],
            options={
                'verbose_name': 'Teologia',
                'verbose_name_plural': 'Skills - THEOLOGY',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('rules.skill',),
        ),
        migrations.CreateModel(
            name='HistorySkill',
            fields=[
            ],
            options={
                'verbose_name': 'Historia',
                'verbose_name_plural': 'Skills - HISTORY',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('rules.skill',),
        ),
        migrations.CreateModel(
            name='WeaponType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True, max_length=4000, null=True)),
                ('sorting_name', models.CharField(blank=True, max_length=250, null=True)),
            ],
            options={
                'verbose_name': 'Weapon type',
                'verbose_name_plural': 'Weapon types',
                'ordering': ['sorting_name'],
            },
        ),
        migrations.CreateModel(
            name='Profession',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True, max_length=4000, null=True)),
                ('sorting_name', models.CharField(blank=True, max_length=250, null=True)),
            ],
            options={
                'verbose_name': 'Profession',
                'verbose_name_plural': 'Professions',
                'ordering': ['sorting_name'],
            },
        ),
        migrations.CreateModel(
            name='EliteKlass',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True, max_length=4000, null=True)),
                ('start_perks', models.TextField(blank=True, max_length=4000, null=True)),
                ('sorting_name', models.CharField(blank=True, max_length=250, null=True)),
                ('allowed_profiles', models.ManyToManyField(blank=True, limit_choices_to=models.Q(status__in=['active_player', 'inactive_player', 'dead_player']), related_name='allowed_elite_klasses', to='users.Profile')),
                ('elite_profession', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='elite_klasses', to='rules.eliteprofession')),
            ],
            options={
                'verbose_name': 'Elite klass',
                'verbose_name_plural': 'Elite klasses',
                'ordering': ['sorting_name'],
            },
        ),
        migrations.CreateModel(
            name='EliteProfession',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True, max_length=4000, null=True)),
                ('sorting_name', models.CharField(blank=True, max_length=250, null=True)),
                ('allowed_profiles', models.ManyToManyField(blank=True, limit_choices_to=models.Q(status__in=['active_player', 'inactive_player', 'dead_player']), related_name='allowed_elite_classes', to='users.Profile')),
            ],
            options={
                'verbose_name': 'Elite profession',
                'verbose_name_plural': 'Elite professions',
                'ordering': ['sorting_name'],
            },
        ),
        migrations.CreateModel(
            name='Klass',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True, max_length=4000, null=True)),
                ('start_perks', models.TextField(blank=True, max_length=4000, null=True)),
                ('lvl_1', models.CharField(blank=True, max_length=500, null=True)),
                ('lvl_2', models.CharField(blank=True, max_length=500, null=True)),
                ('lvl_3', models.CharField(blank=True, max_length=500, null=True)),
                ('lvl_4', models.CharField(blank=True, max_length=500, null=True)),
                ('lvl_5', models.CharField(blank=True, max_length=500, null=True)),
                ('lvl_6', models.CharField(blank=True, max_length=500, null=True)),
                ('lvl_7', models.CharField(blank=True, max_length=500, null=True)),
                ('lvl_8', models.CharField(blank=True, max_length=500, null=True)),
                ('lvl_9', models.CharField(blank=True, max_length=500, null=True)),
                ('lvl_10', models.CharField(blank=True, max_length=500, null=True)),
                ('lvl_11', models.CharField(blank=True, max_length=500, null=True)),
                ('lvl_12', models.CharField(blank=True, max_length=500, null=True)),
                ('lvl_13', models.CharField(blank=True, max_length=500, null=True)),
                ('lvl_14', models.CharField(blank=True, max_length=500, null=True)),
                ('lvl_15', models.CharField(blank=True, max_length=500, null=True)),
                ('lvl_16', models.CharField(blank=True, max_length=500, null=True)),
                ('lvl_17', models.CharField(blank=True, max_length=500, null=True)),
                ('lvl_18', models.CharField(blank=True, max_length=500, null=True)),
                ('lvl_19', models.CharField(blank=True, max_length=500, null=True)),
                ('lvl_20', models.CharField(blank=True, max_length=500, null=True)),
                ('sorting_name', models.CharField(blank=True, max_length=250, null=True)),
                ('allowed_profiles', models.ManyToManyField(blank=True, limit_choices_to=models.Q(status__in=['active_player', 'inactive_player', 'dead_player']), related_name='allowed_klasses', to='users.Profile')),
                ('profession', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='klasses', to='rules.profession')),
            ],
            options={
                'ordering': ['sorting_name'],
                'verbose_name': 'Klass',
                'verbose_name_plural': 'Klasses',
            },
        ),
        migrations.CreateModel(
            name='Plate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True, max_length=4000, null=True)),
                ('armor_class_bonus', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('parrying', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('endurance', models.PositiveSmallIntegerField()),
                ('weight', models.DecimalField(decimal_places=1, max_digits=10)),
                ('mod_max_agility', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('mod_max_movement', models.CharField(blank=True, max_length=2, null=True)),
                ('mod_pickpocketing', models.DecimalField(blank=True, decimal_places=2, max_digits=3, null=True)),
                ('mod_lockpicking', models.DecimalField(blank=True, decimal_places=2, max_digits=3, null=True)),
                ('mod_sneaking_towns', models.DecimalField(blank=True, decimal_places=2, max_digits=3, null=True)),
                ('mod_sneaking_wilderness', models.DecimalField(blank=True, decimal_places=2, max_digits=3, null=True)),
                ('mod_hiding_towns', models.DecimalField(blank=True, decimal_places=2, max_digits=3, null=True)),
                ('mod_hiding_wilderness', models.DecimalField(blank=True, decimal_places=2, max_digits=3, null=True)),
                ('mod_climbing', models.DecimalField(blank=True, decimal_places=2, max_digits=3, null=True)),
                ('mod_traps', models.DecimalField(blank=True, decimal_places=2, max_digits=3, null=True)),
                ('sorting_number', models.DecimalField(decimal_places=2, max_digits=3)),
                ('allowed_profiles', models.ManyToManyField(blank=True, limit_choices_to=models.Q(status__in=['active_player', 'inactive_player', 'dead_player']), related_name='allowed_plates', to='users.Profile')),
                ('pictures', models.ManyToManyField(blank=True, related_name='plate_pics', to='imaginarion.Picture')),
            ],
            options={
                'ordering': ['sorting_number'],
            },
        ),
        migrations.CreateModel(
            name='Shield',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True, max_length=4000, null=True)),
                ('enemies_no', models.PositiveSmallIntegerField()),
                ('armor_class_bonus_close_combat', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('armor_class_bonus_distance_combat', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('weight', models.DecimalField(decimal_places=1, max_digits=10)),
                ('sorting_number', models.DecimalField(decimal_places=2, max_digits=3)),
                ('allowed_profiles', models.ManyToManyField(blank=True, limit_choices_to=models.Q(status__in=['active_player', 'inactive_player', 'dead_player']), related_name='allowed_shields', to='users.Profile')),
                ('pictures', models.ManyToManyField(blank=True, related_name='shield_pics', to='imaginarion.Picture')),
            ],
            options={
                'ordering': ['sorting_number'],
            },
        ),
        migrations.CreateModel(
            name='Weapon',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True, max_length=4000, null=True)),
                ('delay', models.PositiveSmallIntegerField()),
                ('damage_small_dices', models.CharField(blank=True, max_length=10, null=True)),
                ('damage_small_add', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('damage_big_dices', models.CharField(blank=True, max_length=10, null=True)),
                ('damage_big_add', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('damage_type', models.CharField(choices=[('K', 'K'), ('S', 'S'), ('O', 'O'), ('K/S', 'K/S'), ('K/O', 'K/O'), ('O/S', 'O/S'), ('K/S/O', 'K/S/O')], max_length=10)),
                ('special', models.TextField(blank=True, max_length=4000, null=True)),
                ('range', models.CharField(blank=True, max_length=100, null=True)),
                ('size', models.CharField(choices=[('M', 'M'), ('Ś', 'Ś'), ('D', 'D')], max_length=5)),
                ('trait', models.CharField(choices=[('Sił', 'Sił'), ('Zrc', 'Zrc'), ('Sił/Zrc', 'Sił/Zrc')], max_length=10)),
                ('avg_price_value', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('avg_price_currency', models.CharField(blank=True, choices=[('m', 'm'), ('ss', 'ss'), ('sz', 'sz'), ('sp', 'sp')], max_length=5, null=True)),
                ('avg_weight', models.DecimalField(decimal_places=1, max_digits=10)),
                ('sorting_name', models.CharField(blank=True, max_length=250, null=True)),
                ('allowed_profiles', models.ManyToManyField(blank=True, limit_choices_to=models.Q(status__in=['active_player', 'inactive_player', 'dead_player']), related_name='allowed_weapons', to='users.Profile')),
                ('pictures', models.ManyToManyField(blank=True, related_name='weapon_pics', to='imaginarion.Picture')),
                ('weapon_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='weapons', to='rules.weapontype')),
            ],
            options={
                'ordering': ['sorting_name'],
            },
        ),
    ]
