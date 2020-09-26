# Generated by Django 3.1 on 2020-09-26 09:43

from django.db import migrations


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('rules', '0008_auto_20200926_1129'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='WeaponClass',
            new_name='WeaponType',
        ),
        migrations.AlterModelOptions(
            name='weapontype',
            options={'ordering': ['sorting_name'], 'verbose_name': 'Weapon type', 'verbose_name_plural': 'Weapon types'},
        ),
        migrations.RenameField(
            model_name='weapon',
            old_name='weapon_class',
            new_name='weapon_type',
        ),
    ]
