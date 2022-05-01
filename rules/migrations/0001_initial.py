# Generated by Django 4.0.4 on 2022-05-01 06:11

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial_squashed'),
        ('imaginarion', '0001_initial_squashed'),
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
                ('allowed_profiles', models.ManyToManyField(blank=True, limit_choices_to=models.Q(('status', 'player')), related_name='allowed_skills', to='users.profile')),
            ],
            options={
                'ordering': ['sorting_name'],
            },
        ),
        migrations.CreateModel(
            name='Synergy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('sorting_name', models.CharField(blank=True, max_length=250, null=True)),
                ('skills', models.ManyToManyField(related_name='skills', to='rules.skill')),
            ],
            options={
                'verbose_name': 'Synergy',
                'verbose_name_plural': 'Synergies',
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
                ('sorting_name', models.CharField(blank=True, max_length=250, null=True)),
            ],
            options={
                'verbose_name': 'Weapon type',
                'verbose_name_plural': 'Weapon types',
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
            ],
            options={
                'verbose_name': 'Elite profession',
                'verbose_name_plural': 'Elite professions',
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
                ('allowees', models.ManyToManyField(blank=True, limit_choices_to=models.Q(('status__in', ['player', 'gm'])), related_name='allowed_elite_klasses', to='users.profile')),
                ('elite_profession', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='elite_klasses', to='rules.eliteprofession')),
            ],
            options={
                'verbose_name': 'Elite klass',
                'verbose_name_plural': 'Elite klasses',
                'ordering': ['sorting_name'],
            },
        ),
        migrations.CreateModel(
            name='Weapon',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True, max_length=4000, null=True)),
                ('damage_dices', models.CharField(blank=True, max_length=10, null=True)),
                ('damage_bonus', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('damage_type', models.CharField(choices=[('K', 'K'), ('S', 'S'), ('O', 'O'), ('K/S', 'K/S'), ('K/O', 'K/O'), ('O/S', 'O/S'), ('K/S/O', 'K/S/O')], max_length=10)),
                ('special', models.TextField(blank=True, max_length=4000, null=True)),
                ('range', models.CharField(blank=True, max_length=100, null=True)),
                ('size', models.CharField(choices=[('M', 'M'), ('Ś', 'Ś'), ('D', 'D')], max_length=5)),
                ('trait', models.CharField(choices=[('Sił', 'Sił'), ('Zrc', 'Zrc'), ('Sił/Zrc', 'Sił/Zrc')], max_length=10)),
                ('avg_price_value', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('avg_price_currency', models.CharField(blank=True, choices=[('m', 'm'), ('ss', 'ss'), ('sz', 'sz'), ('sp', 'sp')], max_length=5, null=True)),
                ('avg_weight', models.DecimalField(decimal_places=1, max_digits=10)),
                ('sorting_name', models.CharField(blank=True, max_length=250, null=True)),
                ('allowees', models.ManyToManyField(blank=True, limit_choices_to=models.Q(('status__in', ['player', 'gm'])), related_name='allowed_weapons', to='users.profile')),
                ('weapon_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='weapons', to='rules.weapontype')),
                ('picture_set', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='weapons', to='imaginarion.pictureset')),
            ],
            options={
                'ordering': ['sorting_name'],
            },
        ),
        migrations.CreateModel(
            name='SkillType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kind', models.CharField(choices=[('Powszechne', 'Powszechne'), ('Kapłańskie', 'Kapłańskie'), ('Magiczne', 'Magiczne')], default='Powszechne', max_length=100)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('sorting_name', models.CharField(blank=True, max_length=101, null=True)),
            ],
            options={
                'ordering': ['kind', 'sorting_name'],
            },
        ),
        migrations.AddField(
            model_name='skill',
            name='types',
            field=models.ManyToManyField(blank=True, related_name='skills', to='rules.skilltype'),
        ),
        migrations.CreateModel(
            name='Factor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Modifier',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('factor', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='modifiers', to='rules.factor')),
                ('sign', models.CharField(blank=True, choices=[('-', '-'), ('+', '+')], default='+', max_length=1, null=True)),
                ('value_number', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('value_percent', models.DecimalField(blank=True, decimal_places=2, max_digits=3, null=True, validators=[django.core.validators.MinValueValidator(0.01), django.core.validators.MaxValueValidator(1.0)])),
                ('value_text', models.CharField(blank=True, max_length=30, null=True)),
                ('overview', models.CharField(blank=True, max_length=100, null=True)),
            ],
            options={
                'ordering': ['factor', 'sign', 'value_number', 'value_percent', 'value_text'],
                'unique_together': {('factor', 'sign', 'value_number'), ('factor', 'sign', 'value_text'), ('factor', 'sign', 'value_percent')},
            },
        ),
        migrations.CreateModel(
            name='SkillGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.AddField(
            model_name='skill',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='skills', to='rules.skillgroup'),
        ),
        migrations.AlterField(
            model_name='skill',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='skill',
            name='tested_trait',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.CreateModel(
            name='SkillKind',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('sorting_name', models.CharField(blank=True, max_length=101, null=True)),
            ],
            options={
                'ordering': ['sorting_name'],
            },
        ),
        migrations.AddField(
            model_name='skilltype',
            name='kinds',
            field=models.ManyToManyField(blank=True, related_name='skill_types', to='rules.skillkind'),
        ),
        migrations.AlterModelOptions(
            name='skilltype',
            options={'ordering': ['sorting_name']},
        ),
        migrations.RemoveField(
            model_name='skilltype',
            name='kind',
        ),
        migrations.AddField(
            model_name='skillgroup',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='skill_groups', to='rules.skilltype'),
        ),
        migrations.CreateModel(
            name='RulesComment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
            ],
            options={
                'ordering': ['text'],
            },
        ),
        migrations.CreateModel(
            name='Perk',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('description', models.TextField(blank=True, max_length=4000, null=True)),
                ('cost', models.CharField(blank=True, max_length=200, null=True)),
                ('comments', models.ManyToManyField(blank=True, related_name='perks', to='rules.rulescomment')),
                ('conditional_modifiers', models.ManyToManyField(blank=True, related_name='perks', to='rules.conditionalmodifier')),
            ],
            options={
                'ordering': ['name', 'description'],
            },
        ),
        migrations.CreateModel(
            name='SkillLevel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.CharField(choices=[('0', '0'), ('1', '1'), ('2', '2'), ('3', '3')], max_length=10)),
                ('description', models.TextField(blank=True, max_length=4000, null=True)),
                ('sorting_name', models.CharField(blank=True, max_length=250, null=True)),
                ('acquired_by', models.ManyToManyField(blank=True, related_name='skill_levels', to='users.profile')),
                ('skill', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='skill_levels', to='rules.skill')),
                ('perks', models.ManyToManyField(blank=True, related_name='skill_levels', to='rules.perk')),
                ('is_version', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['sorting_name', 'id'],
            },
        ),
        migrations.CreateModel(
            name='SynergyLevel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.CharField(choices=[('1', '1'), ('2', '2'), ('3', '3')], max_length=10)),
                ('description', models.TextField(blank=True, max_length=4000, null=True)),
                ('sorting_name', models.CharField(blank=True, max_length=250, null=True)),
                ('acquired_by', models.ManyToManyField(blank=True, related_name='synergy_levels', to='users.profile')),
                ('synergy', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='synergy_levels', to='rules.synergy')),
                ('perks', models.ManyToManyField(blank=True, related_name='synergy_levels', to='rules.perk')),
                ('skill_levels', models.ManyToManyField(related_name='synergy_levels', to='rules.skilllevel')),
            ],
            options={
                'ordering': ['sorting_name'],
            },
        ),
        migrations.CreateModel(
            name='CombatType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Condition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=200, unique=True)),
            ],
            options={
                'ordering': ['text'],
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
                ('mod_pickpocketing', models.SmallIntegerField(blank=True, null=True)),
                ('mod_lockpicking', models.SmallIntegerField(blank=True, null=True)),
                ('mod_sneaking', models.SmallIntegerField(blank=True, null=True)),
                ('mod_hiding', models.SmallIntegerField(blank=True, null=True)),
                ('mod_climbing', models.SmallIntegerField(blank=True, null=True)),
                ('mod_traps', models.SmallIntegerField(blank=True, null=True)),
                ('sorting_number', models.DecimalField(decimal_places=2, max_digits=3)),
                ('allowees', models.ManyToManyField(blank=True, limit_choices_to=models.Q(('status__in', ['player', 'gm'])), related_name='allowed_plates', to='users.profile')),
                ('comment', models.TextField(blank=True, max_length=200, null=True)),
                ('mod_conning', models.SmallIntegerField(blank=True, null=True)),
                ('mod_listening', models.SmallIntegerField(blank=True, null=True)),
                ('mod_lookout', models.SmallIntegerField(blank=True, null=True)),
                ('mod_running', models.SmallIntegerField(blank=True, null=True)),
                ('mod_swimming', models.SmallIntegerField(blank=True, null=True)),
                ('mod_trailing', models.SmallIntegerField(blank=True, null=True)),
                ('picture_set', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='plates', to='imaginarion.pictureset')),
            ],
            options={
                'ordering': ['sorting_number'],
            },
        ),
        migrations.RenameField(
            model_name='skill',
            old_name='allowed_profiles',
            new_name='allowees',
        ),
        migrations.AlterField(
            model_name='skill',
            name='allowees',
            field=models.ManyToManyField(blank=True, limit_choices_to=models.Q(('status__in', ['player', 'gm'])), related_name='allowed_skills', to='users.profile'),
        ),
        migrations.CreateModel(
            name='ConditionalModifier',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('combat_types', models.ManyToManyField(blank=True, related_name='conditional_modifiers', to='rules.combattype')),
                ('conditions', models.ManyToManyField(blank=True, related_name='conditional_modifiers', to='rules.condition')),
                ('modifier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='conditional_modifiers', to='rules.modifier')),
                ('overview', models.CharField(blank=True, max_length=100, null=True)),
            ],
            options={
                'ordering': ['modifier'],
            },
        ),
        migrations.CreateModel(
            name='Shield',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True, max_length=4000, null=True)),
                ('weight', models.DecimalField(decimal_places=1, max_digits=10)),
                ('sorting_number', models.DecimalField(decimal_places=2, max_digits=3)),
                ('allowees', models.ManyToManyField(blank=True, limit_choices_to=models.Q(('status__in', ['player', 'gm'])), related_name='allowed_shields', to='users.profile')),
                ('armor_class_bonus', models.PositiveSmallIntegerField()),
                ('comment', models.TextField(blank=True, max_length=200, null=True)),
                ('picture_set', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='shields', to='imaginarion.pictureset')),
            ],
            options={
                'ordering': ['sorting_number'],
            },
        ),
        migrations.CreateModel(
            name='Klass',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True, max_length=4000, null=True)),
                ('start_perks', models.TextField(blank=True, max_length=4000, null=True)),
                ('sorting_name', models.CharField(blank=True, max_length=250, null=True)),
            ],
            options={
                'ordering': ['sorting_name'],
                'verbose_name': 'Klass',
                'verbose_name_plural': 'Klasses',
            },
        ),
        migrations.CreateModel(
            name='Profession',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True, max_length=4000, null=True)),
                ('sorting_name', models.CharField(blank=True, max_length=250, null=True)),
                ('allowees', models.ManyToManyField(blank=True, related_name='professions_allowed', to='users.profile')),
                ('type', models.CharField(choices=[('Pospolite', 'Pospolite'), ('Elitarne', 'Elitarne'), ('Hermetyczne', 'Hermetyczne')], max_length=50)),
            ],
            options={
                'verbose_name': 'Profession',
                'verbose_name_plural': '--- PROFESSIONS',
                'ordering': ['sorting_name'],
            },
        ),
        migrations.CreateModel(
            name='SubProfession',
            fields=[
            ],
            options={
                'verbose_name': '--- SubProfession',
                'verbose_name_plural': '--- SubProfessions',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('rules.profession',),
        ),
        migrations.DeleteModel(
            name='SubProfession',
        ),
        migrations.CreateModel(
            name='PrimaryProfession',
            fields=[
            ],
            options={
                'verbose_name': 'Primary Profession',
                'verbose_name_plural': '--- Primary Professions',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('rules.profession',),
        ),
        migrations.CreateModel(
            name='SecondaryProfession',
            fields=[
            ],
            options={
                'verbose_name': 'Secondary Profession',
                'verbose_name_plural': '--- Secondary Professions',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('rules.profession',),
        ),
        migrations.DeleteModel(
            name='EliteKlass',
        ),
        migrations.DeleteModel(
            name='EliteProfession',
        ),
        migrations.DeleteModel(
            name='Klass',
        ),
        migrations.CreateModel(
            name='SubProfession',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True, max_length=4000, null=True)),
                ('sorting_name', models.CharField(blank=True, max_length=250, null=True)),
                ('allowees', models.ManyToManyField(blank=True, related_name='subprofessions_allowed', to='users.profile')),
                ('profession', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='subprofessions', to='rules.profession')),
                ('essential_skills', models.ManyToManyField(blank=True, to='rules.skill')),
            ],
            options={
                'verbose_name': 'SubProfession',
                'verbose_name_plural': '--- SUBPROFESSIONS',
                'ordering': ['sorting_name'],
            },
        ),
        migrations.DeleteModel(
            name='PrimaryProfession',
        ),
        migrations.DeleteModel(
            name='SecondaryProfession',
        ),
        migrations.CreateModel(
            name='Sphragis',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='skill',
            name='is_version',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='skill',
            name='weapon',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='rules.weapon'),
        ),
        migrations.AddField(
            model_name='skill',
            name='sphragis',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='rules.sphragis'),
        ),
    ]
