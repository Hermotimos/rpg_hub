# Generated by Django 2.2.1 on 2019-07-18 18:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20190718_2011'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='profile',
            options={'ordering': ['id', 'character_name']},
        ),
    ]
