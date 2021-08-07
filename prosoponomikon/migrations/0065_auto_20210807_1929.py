# Generated by Django 3.1 on 2021-08-07 17:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_auto_20210309_1955'),
        ('prosoponomikon', '0064_auto_20210807_1249'),
    ]

    operations = [
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
    ]
