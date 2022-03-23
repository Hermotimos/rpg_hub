# Generated by Django 4.0.2 on 2022-03-20 19:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    # replaces = [('prosoponomikon', '0001_initial'), ('prosoponomikon', '0002_auto_20201225_2018'), ('prosoponomikon', '0003_auto_20201225_2018'), ('prosoponomikon', '0004_character_descr_psychophysical'), ('prosoponomikon', '0005_character_descr_for_gm'), ('prosoponomikon', '0006_auto_20201225_2108'), ('prosoponomikon', '0007_auto_20201226_1050'), ('prosoponomikon', '0008_auto_20201226_1055'), ('prosoponomikon', '0009_auto_20201226_2252'), ('prosoponomikon', '0010_auto_20210103_0524'), ('prosoponomikon', '0011_auto_20210103_0537'), ('prosoponomikon', '0012_auto_20210103_0647'), ('prosoponomikon', '0013_auto_20210103_0653'), ('prosoponomikon', '0014_auto_20210103_1358'), ('prosoponomikon', '0015_auto_20210106_1613'), ('prosoponomikon', '0016_auto_20210106_1852'), ('prosoponomikon', '0017_character_charactergroup_npccharacter_playercharacter'), ('prosoponomikon', '0018_auto_20210117_1618'), ('prosoponomikon', '0019_character_charactergroup_npccharacter_playercharacter'), ('prosoponomikon', '0020_auto_20210117_1651'), ('prosoponomikon', '0021_auto_20210131_1139'), ('prosoponomikon', '0022_auto_20210131_1902'), ('prosoponomikon', '0023_auto_20210220_1123'), ('prosoponomikon', '0024_character_cognomen'), ('prosoponomikon', '0025_auto_20210221_1554'), ('prosoponomikon', '0026_auto_20210221_1558'), ('prosoponomikon', '0027_namecontinuum_nameform'), ('prosoponomikon', '0028_auto_20210221_1619'), ('prosoponomikon', '0029_auto_20210221_1632'), ('prosoponomikon', '0030_auto_20210221_1642'), ('prosoponomikon', '0031_nameform_type'), ('prosoponomikon', '0032_auto_20210221_1808'), ('prosoponomikon', '0033_auto_20210221_1943'), ('prosoponomikon', '0034_auto_20210223_2005'), ('prosoponomikon', '0035_auto_20210225_2010'), ('prosoponomikon', '0036_auto_20210225_2026'), ('prosoponomikon', '0037_auto_20210226_1740'), ('prosoponomikon', '0038_auto_20210227_0001'), ('prosoponomikon', '0039_auto_20210305_1323'), ('prosoponomikon', '0040_auto_20210305_1325'), ('prosoponomikon', '0041_auto_20210305_1326'), ('prosoponomikon', '0042_auto_20210305_1421'), ('prosoponomikon', '0043_auto_20210305_1504'), ('prosoponomikon', '0044_auto_20210305_1513'), ('prosoponomikon', '0045_auto_20210305_1612'), ('prosoponomikon', '0046_auto_20210308_2009'), ('prosoponomikon', '0047_auto_20210310_1828'), ('prosoponomikon', '0048_auto_20210310_1831'), ('prosoponomikon', '0049_auto_20210310_1832'), ('prosoponomikon', '0050_auto_20210310_1902'), ('prosoponomikon', '0051_auto_20210310_1921'), ('prosoponomikon', '0052_auto_20210311_2137'), ('prosoponomikon', '0053_auto_20210312_1153'), ('prosoponomikon', '0054_auto_20210312_2133'), ('prosoponomikon', '0055_auto_20210318_2315'), ('prosoponomikon', '0056_firstname_form_2'), ('prosoponomikon', '0057_namegroup_type'), ('prosoponomikon', '0058_auto_20210319_0943'), ('prosoponomikon', '0059_auto_20210320_1417'), ('prosoponomikon', '0060_familyname_auxiliary_group'), ('prosoponomikon', '0061_remove_familyname_auxiliary_group'), ('prosoponomikon', '0062_auto_20210320_1809'), ('prosoponomikon', '0063_familyname_info'), ('prosoponomikon', '0064_auto_20210807_1249'), ('prosoponomikon', '0065_auto_20210807_1929'), ('prosoponomikon', '0066_remove_character_pictures'), ('prosoponomikon', '0067_auto_20211017_1835'), ('prosoponomikon', '0068_character_professions'), ('prosoponomikon', '0069_delete_charactergroup')]

    initial = True

    dependencies = [
        ('knowledge', '0018_auto_20211017_1835'),
        ('knowledge', '0002_auto_20201225_1400'),
        ('users', '0002_auto_20201225_1757'),
        ('rules', '0002_auto_20210106_1613'),
        ('users', '0003_auto_20210103_0647'),
        ('knowledge', '0011_auto_20210221_1423'),
        ('knowledge', '0003_auto_20201226_2252'),
        ('users', '0007_auto_20210106_1613'),
        ('rules', '0059_alter_conditionalmodifier_options'),
        ('knowledge', '0004_auto_20201228_2101'),
        ('users', '0008_auto_20210309_1955'),
        ('knowledge', '0005_biographypacket_show_in_prosoponomikon'),
        ('toponomikon', '0001_0001_initial_squashed'),
        ('rules', '0005_auto_20211017_1835'),
        ('knowledge', '0006_remove_biographypacket_show_in_prosoponomikon'),
        ('imaginarion', '0001_initial'),
        # ('toponomikon', '0001_initial'),
        ('imaginarion', '0002_auto_20210103_1049'),
    ]

    operations = [
        migrations.CreateModel(
            name='Character',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description_main', models.TextField(blank=True, null=True)),
                ('sorting_name', models.CharField(blank=True, max_length=250, null=True)),
            ],
            options={
                'ordering': ['sorting_name'],
            },
        ),
        migrations.CreateModel(
            name='NonPlayerCharacter',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('prosoponomikon.character',),
        ),
        migrations.CreateModel(
            name='PlayerCharacter',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('prosoponomikon.character',),
        ),
        migrations.CreateModel(
            name='Persona',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
                ('sorting_name', models.CharField(blank=True, max_length=250, null=True)),
            ],
            options={
                'ordering': ['sorting_name'],
                'verbose_name': '* PERSONAS',
                'verbose_name_plural': '* PERSONAS',
            },
        ),
        migrations.CreateModel(
            name='PersonaGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250, verbose_name='Nazwa grupy')),
                ('order_no', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Numer porządkowy grupy [opcjonalnie]')),
            ],
            options={
                'ordering': ['order_no', 'name'],
                'verbose_name': '* PERSONA GROUP',
                'verbose_name_plural': '* PERSONA GROUPS',
            },
        ),
        migrations.CreateModel(
            name='CharacterGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250, verbose_name='Nazwa grupy')),
                ('order_no', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Numer porządkowy grupy [opcjonalnie]:')),
            ],
            options={
                'ordering': ['order_no', 'name'],
            },
        ),
        migrations.DeleteModel(
            name='NonPlayerCharacter',
        ),
        migrations.DeleteModel(
            name='PlayerCharacter',
        ),
        migrations.DeleteModel(
            name='Character',
        ),
        migrations.DeleteModel(
            name='CharacterGroup',
        ),
        migrations.CreateModel(
            name='NonPlayerPersona',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
                'verbose_name': '--- NPC',
                'verbose_name_plural': '--- NPCs',
            },
            bases=('prosoponomikon.persona',),
        ),
        migrations.CreateModel(
            name='PlayerPersona',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
                'verbose_name': '--- Player',
                'verbose_name_plural': '--- Players',
            },
            bases=('prosoponomikon.persona',),
        ),
        migrations.DeleteModel(
            name='NonPlayerPersona',
        ),
        migrations.CreateModel(
            name='NPCPersona',
            fields=[
            ],
            options={
                'verbose_name': '--- NPC',
                'verbose_name_plural': '--- NPCs',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('prosoponomikon.persona',),
        ),
        migrations.CreateModel(
            name='Character',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
                ('sorting_name', models.CharField(blank=True, max_length=250, null=True)),
            ],
            options={
                'verbose_name': '* CHARACTER',
                'verbose_name_plural': '* CHARACTERS',
                'ordering': ['sorting_name'],
            },
        ),
        migrations.CreateModel(
            name='NPCCharacter',
            fields=[
            ],
            options={
                'verbose_name': '--- NPC',
                'verbose_name_plural': '--- NPCs',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('prosoponomikon.character',),
        ),
        migrations.CreateModel(
            name='PlayerCharacter',
            fields=[
            ],
            options={
                'verbose_name': '--- Player',
                'verbose_name_plural': '--- Players',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('prosoponomikon.character',),
        ),
        migrations.CreateModel(
            name='CharacterGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250, verbose_name='Nazwa grupy')),
                ('order_no', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Numer porządkowy grupy [opcjonalnie]')),
            ],
            options={
                'verbose_name': '* CHARACTER GROUP',
                'verbose_name_plural': '* CHARACTER GROUPS',
                'ordering': ['order_no', 'name'],
            },
        ),
        migrations.DeleteModel(
            name='NPCCharacter',
        ),
        migrations.DeleteModel(
            name='PlayerCharacter',
        ),
        migrations.DeleteModel(
            name='Character',
        ),
        migrations.DeleteModel(
            name='CharacterGroup',
        ),
        migrations.CreateModel(
            name='Character',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.IntegerField(blank=True, max_length=100, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('sorting_name', models.CharField(blank=True, max_length=250, null=True)),
                ('biography_packets', models.ManyToManyField(blank=True, related_name='characters', to='knowledge.BiographyPacket')),
                ('dialogue_packets', models.ManyToManyField(blank=True, related_name='characters', to='knowledge.DialoguePacket')),
                ('frequented_locations', models.ManyToManyField(blank=True, related_name='frequented_by_characters', to='toponomikon.Location')),
                ('known_directly', models.ManyToManyField(blank=True, limit_choices_to=models.Q(('status', 'player')), related_name='characters_known_directly', to='users.Profile')),
                ('known_indirectly', models.ManyToManyField(blank=True, limit_choices_to=models.Q(('status', 'player')), related_name='characters_known_indirectly', to='users.Profile')),
                ('pictures', models.ManyToManyField(blank=True, related_name='characters', to='imaginarion.Picture')),
                ('profile', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='users.profile')),
                ('cognomen', models.CharField(blank=True, max_length=250, null=True)),
            ],
            options={
                'verbose_name': '* CHARACTER',
                'verbose_name_plural': '* CHARACTERS',
                'ordering': ['sorting_name'],
            },
        ),
        migrations.CreateModel(
            name='CharacterGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250, verbose_name='Nazwa grupy')),
                ('order_no', models.SmallIntegerField(default=1, verbose_name='Nr porządkowy')),
                ('author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='character_groups_authored', to='users.profile')),
                ('characters', models.ManyToManyField(related_name='character_groups', to='prosoponomikon.Character', verbose_name='Zgrupowane postacie')),
                ('default_knowledge_packets', models.ManyToManyField(blank=True, related_name='character_group_defaults', to='knowledge.KnowledgePacket', verbose_name='Domyślne pakiety wiedzy NPC w grupie')),
                ('default_skills', models.ManyToManyField(blank=True, related_name='character_group_defaults', to='rules.Skill', verbose_name='Domyślne umiejętności NPC w grupie')),
            ],
            options={
                'verbose_name': '* CHARACTER GROUP',
                'verbose_name_plural': '* CHARACTER GROUPS',
                'ordering': ['order_no', 'name'],
                'unique_together': {('name', 'author')},
            },
        ),
        migrations.CreateModel(
            name='NPCCharacter',
            fields=[
            ],
            options={
                'verbose_name': '--- NPC',
                'verbose_name_plural': '--- NPCs',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('prosoponomikon.character',),
        ),
        migrations.CreateModel(
            name='PlayerCharacter',
            fields=[
            ],
            options={
                'verbose_name': '--- Player',
                'verbose_name_plural': '--- Players',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('prosoponomikon.character',),
        ),
        migrations.DeleteModel(
            name='NPCPersona',
        ),
        migrations.DeleteModel(
            name='PlayerPersona',
        ),
        migrations.DeleteModel(
            name='Persona',
        ),
        migrations.DeleteModel(
            name='PersonaGroup',
        ),
        migrations.CreateModel(
            name='NameGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=250, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('type', models.CharField(choices=[('local', 'local'), ('racial', 'racial'), ('social', 'social')], max_length=50)),
            ],
            options={
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='FamilyName',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('form', models.CharField(max_length=250, unique=True)),
                ('locations', models.ManyToManyField(blank=True, related_name='family_names', to='toponomikon.Location')),
            ],
            options={
                'ordering': ['group', 'form'],
            },
        ),
        migrations.AddField(
            model_name='character',
            name='family_name',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='characters', to='prosoponomikon.familyname'),
        ),
        migrations.CreateModel(
            name='Name',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('form', models.CharField(max_length=250, unique=True)),
                ('is_ancient', models.BooleanField(default=False)),
                ('type', models.CharField(choices=[('MALE', 'MALE'), ('FEMALE', 'FEMALE'), ('DAEMON', 'DAEMON')], default='male', max_length=20)),
            ],
            options={
                'ordering': ['form'],
            },
        ),
        migrations.RenameField(
            model_name='character',
            old_name='name',
            new_name='first_name',
        ),
        migrations.AlterField(
            model_name='character',
            name='first_name',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='characters', to='prosoponomikon.nameform'),
        ),
        migrations.AlterField(
            model_name='character',
            name='first_name',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='character',
            name='first_name',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='characters', to='prosoponomikon.name'),
        ),
        migrations.CreateModel(
            name='AffixGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('affix', models.CharField(max_length=100)),
                ('name_group', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='affix_groups', to='prosoponomikon.namegroup')),
                ('type', models.CharField(choices=[('MALE', 'MALE'), ('FEMALE', 'FEMALE'), ('UNISEX', 'UNISEX')], default='MALE', max_length=20)),
            ],
            options={
                'ordering': ['name_group', 'type', 'affix'],
                'unique_together': {('affix', 'type', 'name_group')},
            },
        ),
        migrations.CreateModel(
            name='AuxiliaryNameGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('color', models.CharField(blank=True, max_length=100, null=True)),
                ('social_info', models.TextField(blank=True, help_text='Social group indication if no location', null=True)),
                ('location', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='toponomikon.location')),
            ],
            options={
                'ordering': ['social_info', 'location'],
            },
        ),
        migrations.AddField(
            model_name='name',
            name='auxiliary_group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='prosoponomikon.auxiliarynamegroup'),
        ),
        migrations.AddField(
            model_name='name',
            name='affix_group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='names', to='prosoponomikon.affixgroup'),
        ),
        migrations.RemoveField(
            model_name='name',
            name='type',
        ),
        migrations.RenameModel(
            old_name='Name',
            new_name='FirstName',
        ),
        migrations.AlterField(
            model_name='character',
            name='first_name',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='character',
            name='first_name',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='characters', to='prosoponomikon.firstname'),
        ),
        migrations.AddField(
            model_name='firstname',
            name='info',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='firstname',
            name='affix_group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='first_names', to='prosoponomikon.affixgroup'),
        ),
        migrations.AlterModelOptions(
            name='firstname',
            options={'ordering': ['auxiliary_group', 'form']},
        ),
        migrations.AddField(
            model_name='firstname',
            name='form_2',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.CreateModel(
            name='FamilyNameGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=250, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
            ],
            options={
                'ordering': ['title'],
            },
        ),
        migrations.AddField(
            model_name='familyname',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='prosoponomikon.familynamegroup'),
        ),
        migrations.AddField(
            model_name='familyname',
            name='info',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='NonGMCharacter',
            fields=[
            ],
            options={
                'verbose_name': '--- Player or NPC',
                'verbose_name_plural': '--- Players and NPCs',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('prosoponomikon.character',),
        ),
        migrations.AlterField(
            model_name='character',
            name='known_directly',
            field=models.ManyToManyField(blank=True, related_name='characters_known_directly', to='users.Profile'),
        ),
        migrations.AlterField(
            model_name='character',
            name='known_indirectly',
            field=models.ManyToManyField(blank=True, related_name='characters_known_indirectly', to='users.Profile'),
        ),
        migrations.RemoveField(
            model_name='character',
            name='pictures',
        ),
        migrations.AlterField(
            model_name='charactergroup',
            name='characters',
            field=models.ManyToManyField(related_name='character_groups', to='prosoponomikon.Character'),
        ),
        migrations.AlterField(
            model_name='charactergroup',
            name='default_knowledge_packets',
            field=models.ManyToManyField(blank=True, related_name='character_group_defaults', to='knowledge.KnowledgePacket'),
        ),
        migrations.AlterField(
            model_name='charactergroup',
            name='default_skills',
            field=models.ManyToManyField(blank=True, related_name='character_group_defaults', to='rules.Skill'),
        ),
        migrations.AlterField(
            model_name='charactergroup',
            name='name',
            field=models.CharField(max_length=250),
        ),
        migrations.AlterField(
            model_name='charactergroup',
            name='order_no',
            field=models.SmallIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='character',
            name='professions',
            field=models.ManyToManyField(blank=True, related_name='characters', to='rules.Profession'),
        ),
        migrations.DeleteModel(
            name='CharacterGroup',
        ),
    ]
