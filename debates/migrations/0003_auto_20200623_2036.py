# Generated by Django 2.2.1 on 2020-06-23 18:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('debates', '0002_remove_debate_starter'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='debate',
            options={'ordering': ['date_created']},
        ),
        migrations.AlterModelOptions(
            name='topic',
            options={'ordering': ['title']},
        ),
    ]
