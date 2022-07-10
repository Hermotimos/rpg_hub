# Generated by Django 4.0.4 on 2022-07-10 12:40

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('imaginarion', '0004_alter_pictureimage_image'),
        ('users', '0001_initial'),
    ]

    operations = [
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
            name='ConditionalModifier',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('combat_types', models.ManyToManyField(blank=True, related_name='conditional_modifiers', to='rules.combattype')),
                ('conditions', models.ManyToManyField(blank=True, related_name='conditional_modifiers', to='rules.condition')),
            ],
            options={
                'ordering': ['modifier'],
            },
        ),
        migrations.CreateModel(
            name='DamageType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(blank=True, max_length=30, null=True)),
                ('type', models.CharField(choices=[('K', 'K'), ('S', 'S'), ('O', 'O'), ('K/S', 'K/S'), ('K/O', 'K/O'), ('O/S', 'O/S'), ('K/S/O', 'K/S/O')], max_length=10)),
                ('damage', models.CharField(max_length=15)),
                ('special', models.CharField(blank=True, max_length=100, null=True)),
            ],
            options={
                'ordering': ['type', 'description'],
                'unique_together': {('description', 'type', 'damage', 'special')},
            },
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
            name='Perk',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('description', models.TextField(blank=True, max_length=4000, null=True)),
                ('cost', models.CharField(blank=True, max_length=200, null=True)),
            ],
            options={
                'ordering': ['name', 'description'],
            },
        ),
        migrations.CreateModel(
            name='Profession',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('type', models.CharField(choices=[('Pospolite', 'Pospolite'), ('Elitarne', 'Elitarne'), ('Hermetyczne', 'Hermetyczne')], max_length=50)),
                ('description', models.TextField(blank=True, max_length=4000, null=True)),
                ('allowees', models.ManyToManyField(blank=True, related_name='professions_allowed', to='users.profile')),
            ],
            options={
                'verbose_name': 'Profession',
                'verbose_name_plural': '--- PROFESSIONS',
                'ordering': ['name'],
            },
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
            name='Skill',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('name_second', models.CharField(blank=True, max_length=100, null=True)),
                ('name_origin', models.CharField(blank=True, max_length=100, null=True)),
                ('tested_trait', models.CharField(blank=True, max_length=50, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='skills')),
                ('allowees', models.ManyToManyField(blank=True, limit_choices_to=models.Q(('status', 'player')), related_name='allowed_skills', to='users.profile')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='SkillKind',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='SkillLevel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.CharField(choices=[('0', '0'), ('1', '1'), ('2', '2'), ('3', '3')], max_length=10)),
                ('description', models.TextField(blank=True, null=True)),
                ('distance', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('radius', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('duration', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('damage', models.CharField(blank=True, max_length=20, null=True)),
                ('saving_throw_malus', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('saving_throw_trait', models.CharField(blank=True, choices=[('Sił', 'Sił'), ('Zrc', 'Zrc'), ('Kon', 'Kon'), ('Sił/Zrc', 'Sił/Zrc'), ('Sił/Kon', 'Sił/Kon'), ('Zrc/Kon', 'Zrc/Kon'), ('Sił/Zrc/Kon', 'Sił/Zrc/Kon')], max_length=20, null=True)),
                ('acquired_by', models.ManyToManyField(blank=True, related_name='skill_levels', to='users.profile')),
                ('perks', models.ManyToManyField(blank=True, related_name='skill_levels', to='rules.perk')),
                ('skill', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='skill_levels', to='rules.skill')),
            ],
            options={
                'ordering': ['skill__name', 'level'],
            },
        ),
        migrations.CreateModel(
            name='Sphragis',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('name_genitive', models.CharField(max_length=100, unique=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Synergy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('skills', models.ManyToManyField(related_name='skills', to='rules.skill')),
            ],
            options={
                'verbose_name': 'Synergy',
                'verbose_name_plural': 'Synergies',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='WeaponType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True, max_length=4000, null=True)),
                ('size', models.CharField(choices=[('M', 'M'), ('Ś', 'Ś'), ('D', 'D')], max_length=5)),
                ('trait', models.CharField(choices=[('Sił', 'Sił'), ('Zrc', 'Zrc'), ('Sił/Zrc', 'Sił/Zrc')], max_length=10)),
                ('avg_price_value', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('avg_price_currency', models.CharField(blank=True, choices=[('m', 'm'), ('ss', 'ss'), ('sz', 'sz'), ('sp', 'sp')], max_length=5, null=True)),
                ('avg_weight', models.DecimalField(decimal_places=1, max_digits=10)),
                ('allowees', models.ManyToManyField(blank=True, limit_choices_to=models.Q(('status', 'player')), related_name='allowed_weapon_types', to='users.profile')),
                ('comparables', models.ManyToManyField(blank=True, to='rules.weapontype')),
                ('damage_types', models.ManyToManyField(related_name='weapon_types', to='rules.damagetype')),
                ('picture_set', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='weapon_types', to='imaginarion.pictureset')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='SynergyLevel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.CharField(choices=[('1', '1'), ('2', '2'), ('3', '3')], max_length=10)),
                ('description', models.TextField(blank=True, max_length=4000, null=True)),
                ('acquired_by', models.ManyToManyField(blank=True, related_name='synergy_levels', to='users.profile')),
                ('perks', models.ManyToManyField(blank=True, related_name='synergy_levels', to='rules.perk')),
                ('skill_levels', models.ManyToManyField(related_name='synergy_levels', to='rules.skilllevel')),
                ('synergy', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='synergy_levels', to='rules.synergy')),
            ],
            options={
                'ordering': ['synergy', 'level'],
            },
        ),
        migrations.CreateModel(
            name='SubProfession',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True, max_length=4000, null=True)),
                ('allowees', models.ManyToManyField(blank=True, related_name='subprofessions_allowed', to='users.profile')),
                ('essential_skills', models.ManyToManyField(blank=True, to='rules.skill')),
                ('profession', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='subprofessions', to='rules.profession')),
            ],
            options={
                'verbose_name': 'SubProfession',
                'verbose_name_plural': '--- SUBPROFESSIONS',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='SkillType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('kinds', models.ManyToManyField(blank=True, related_name='skill_types', to='rules.skillkind')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='SkillGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='skill_groups', to='rules.skilltype')),
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
        migrations.AddField(
            model_name='skill',
            name='types',
            field=models.ManyToManyField(blank=True, related_name='skills', to='rules.skilltype'),
        ),
        migrations.AddField(
            model_name='skill',
            name='version_of',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='versions', to='rules.skill'),
        ),
        migrations.AddField(
            model_name='skill',
            name='weapon',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='rules.weapontype'),
        ),
        migrations.CreateModel(
            name='Shield',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True, max_length=4000, null=True)),
                ('armor_class_bonus', models.PositiveSmallIntegerField()),
                ('weight', models.DecimalField(decimal_places=1, max_digits=10)),
                ('comment', models.TextField(blank=True, max_length=200, null=True)),
                ('sorting_number', models.DecimalField(decimal_places=2, max_digits=3)),
                ('allowees', models.ManyToManyField(blank=True, limit_choices_to=models.Q(('status', 'player')), related_name='allowed_shields', to='users.profile')),
                ('picture_set', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='shields', to='imaginarion.pictureset')),
            ],
            options={
                'ordering': ['sorting_number'],
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
                ('comment', models.TextField(blank=True, max_length=200, null=True)),
                ('mod_running', models.SmallIntegerField(blank=True, null=True)),
                ('mod_swimming', models.SmallIntegerField(blank=True, null=True)),
                ('mod_climbing', models.SmallIntegerField(blank=True, null=True)),
                ('mod_listening', models.SmallIntegerField(blank=True, null=True)),
                ('mod_lookout', models.SmallIntegerField(blank=True, null=True)),
                ('mod_trailing', models.SmallIntegerField(blank=True, null=True)),
                ('mod_sneaking', models.SmallIntegerField(blank=True, null=True)),
                ('mod_hiding', models.SmallIntegerField(blank=True, null=True)),
                ('mod_traps', models.SmallIntegerField(blank=True, null=True)),
                ('mod_lockpicking', models.SmallIntegerField(blank=True, null=True)),
                ('mod_pickpocketing', models.SmallIntegerField(blank=True, null=True)),
                ('mod_conning', models.SmallIntegerField(blank=True, null=True)),
                ('sorting_number', models.DecimalField(decimal_places=2, max_digits=3)),
                ('allowees', models.ManyToManyField(blank=True, limit_choices_to=models.Q(('status', 'player')), related_name='allowed_plates', to='users.profile')),
                ('picture_set', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='plates', to='imaginarion.pictureset')),
            ],
            options={
                'ordering': ['sorting_number'],
            },
        ),
        migrations.AddField(
            model_name='perk',
            name='comments',
            field=models.ManyToManyField(blank=True, related_name='perks', to='rules.rulescomment'),
        ),
        migrations.AddField(
            model_name='perk',
            name='conditional_modifiers',
            field=models.ManyToManyField(blank=True, related_name='perks', to='rules.conditionalmodifier'),
        ),
        migrations.CreateModel(
            name='Modifier',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sign', models.CharField(blank=True, choices=[('-', '-'), ('+', '+')], default='+', max_length=1, null=True)),
                ('value_number', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('value_percent', models.DecimalField(blank=True, decimal_places=2, max_digits=3, null=True, validators=[django.core.validators.MinValueValidator(0.01), django.core.validators.MaxValueValidator(1.0)])),
                ('value_text', models.CharField(blank=True, max_length=30, null=True)),
                ('factor', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='modifiers', to='rules.factor')),
            ],
            options={
                'ordering': ['factor', 'sign', 'value_number', 'value_percent', 'value_text'],
                'unique_together': {('factor', 'sign', 'value_text'), ('factor', 'sign', 'value_percent'), ('factor', 'sign', 'value_number')},
            },
        ),
        migrations.AddField(
            model_name='conditionalmodifier',
            name='modifier',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='conditional_modifiers', to='rules.modifier'),
        ),
        migrations.CreateModel(
            name='MentalSkill',
            fields=[
            ],
            options={
                'verbose_name': 'Skill - MENTALNE',
                'verbose_name_plural': 'Skills - MENTALNE',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('rules.skill',),
        ),
        migrations.CreateModel(
            name='MentalSkillLevel',
            fields=[
            ],
            options={
                'verbose_name': 'Skill Level - MENTALNE',
                'verbose_name_plural': 'Skill Levels - MENTALNE',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('rules.skilllevel',),
        ),
        migrations.CreateModel(
            name='MentalSynergy',
            fields=[
            ],
            options={
                'verbose_name': 'Synergy - MENTALNE',
                'verbose_name_plural': 'Synergies - MENTALNE',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('rules.synergy',),
        ),
        migrations.CreateModel(
            name='MentalSynergyLevel',
            fields=[
            ],
            options={
                'verbose_name': 'Synergy Level - MENTALNE',
                'verbose_name_plural': 'Synergy Levels - MENTALNE',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('rules.synergylevel',),
        ),
        migrations.CreateModel(
            name='PriestsSkill',
            fields=[
            ],
            options={
                'verbose_name': 'Skill - MOCE KAPŁAŃSKIE',
                'verbose_name_plural': 'Skills - MOCE KAPŁAŃSKIE',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('rules.skill',),
        ),
        migrations.CreateModel(
            name='PriestsSkillLevel',
            fields=[
            ],
            options={
                'verbose_name': 'Skill Level - MOCE KAPŁAŃSKIE',
                'verbose_name_plural': 'Skill Levels - MOCE KAPŁAŃSKIE',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('rules.skilllevel',),
        ),
        migrations.CreateModel(
            name='RegularSkill',
            fields=[
            ],
            options={
                'verbose_name': 'Skill - POWSZECHNE',
                'verbose_name_plural': 'Skills - POWSZECHNE',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('rules.skill',),
        ),
        migrations.CreateModel(
            name='RegularSkillLevel',
            fields=[
            ],
            options={
                'verbose_name': 'Skill Level - POWSZECHNE',
                'verbose_name_plural': 'Skill Levels - POWSZECHNE',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('rules.skilllevel',),
        ),
        migrations.CreateModel(
            name='RegularSynergy',
            fields=[
            ],
            options={
                'verbose_name': 'Synergy - POWSZECHNE',
                'verbose_name_plural': 'Synergies - POWSZECHNE',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('rules.synergy',),
        ),
        migrations.CreateModel(
            name='RegularSynergyLevel',
            fields=[
            ],
            options={
                'verbose_name': 'Synergy Level - POWSZECHNE',
                'verbose_name_plural': 'Synergy Levels - POWSZECHNE',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('rules.synergylevel',),
        ),
        migrations.CreateModel(
            name='SorcerersSkill',
            fields=[
            ],
            options={
                'verbose_name': 'Skill - ZAKLĘCIA',
                'verbose_name_plural': 'Skills - ZAKLĘCIA',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('rules.skill',),
        ),
        migrations.CreateModel(
            name='SorcerersSkillLevel',
            fields=[
            ],
            options={
                'verbose_name': 'Skill Level - ZAKLĘCIA',
                'verbose_name_plural': 'Skill Levels - ZAKLĘCIA',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('rules.skilllevel',),
        ),
        migrations.CreateModel(
            name='TheurgistsSkill',
            fields=[
            ],
            options={
                'verbose_name': 'Skill - MOCE TEURGICZNE',
                'verbose_name_plural': 'Skills - MOCE TEURGICZNE',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('rules.skill',),
        ),
        migrations.CreateModel(
            name='TheurgistsSkillLevel',
            fields=[
            ],
            options={
                'verbose_name': 'Skill Level - MOCE TEURGICZNE',
                'verbose_name_plural': 'Skill Levels - MOCE TEURGICZNE',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('rules.skilllevel',),
        ),
    ]
