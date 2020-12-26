# Generated by Django 3.1 on 2020-12-26 21:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('imaginarion', '0001_initial'),
        ('rules', '0001_initial'),
        ('knowledge', '0002_auto_20201225_1400'),
    ]

    operations = [
        migrations.AlterField(
            model_name='biographypacket',
            name='text',
            field=models.TextField(blank=True, null=True, verbose_name='Treść (niewymagane)'),
        ),
        migrations.AlterField(
            model_name='biographypacket',
            name='title',
            field=models.CharField(max_length=100, unique=True, verbose_name='Tytuł'),
        ),
        migrations.AlterField(
            model_name='dialoguepacket',
            name='text',
            field=models.TextField(blank=True, null=True, verbose_name='Treść (niewymagane)'),
        ),
        migrations.AlterField(
            model_name='dialoguepacket',
            name='title',
            field=models.CharField(max_length=100, unique=True, verbose_name='Tytuł'),
        ),
        migrations.AlterField(
            model_name='knowledgepacket',
            name='pictures',
            field=models.ManyToManyField(blank=True, related_name='knowledge_packets', to='imaginarion.Picture', verbose_name='Obrazy [opcjonalnie]:'),
        ),
        migrations.AlterField(
            model_name='knowledgepacket',
            name='skills',
            field=models.ManyToManyField(related_name='knowledge_packets', to='rules.Skill', verbose_name='Umiejętności powiązane'),
        ),
        migrations.AlterField(
            model_name='knowledgepacket',
            name='text',
            field=models.TextField(blank=True, null=True, verbose_name='Treść (niewymagane)'),
        ),
        migrations.AlterField(
            model_name='knowledgepacket',
            name='title',
            field=models.CharField(max_length=100, unique=True, verbose_name='Tytuł'),
        ),
        migrations.AlterField(
            model_name='mappacket',
            name='pictures',
            field=models.ManyToManyField(related_name='map_packets', to='imaginarion.Picture', verbose_name='Obrazy [opcjonalnie]:'),
        ),
        migrations.AlterField(
            model_name='mappacket',
            name='text',
            field=models.TextField(blank=True, null=True, verbose_name='Treść (niewymagane)'),
        ),
        migrations.AlterField(
            model_name='mappacket',
            name='title',
            field=models.CharField(max_length=100, unique=True, verbose_name='Tytuł'),
        ),
    ]
