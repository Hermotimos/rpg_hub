# Generated by Django 3.1 on 2020-09-23 05:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chronicles', '0014_timeunit_debates'),
    ]

    operations = [
        migrations.CreateModel(
            name='ThreadActive',
            fields=[
            ],
            options={
                'verbose_name': '- Active Thread',
                'verbose_name_plural': '- Threads Active',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('chronicles.thread',),
        ),
        migrations.CreateModel(
            name='ThreadEnded',
            fields=[
            ],
            options={
                'verbose_name': '- Ended Thread',
                'verbose_name_plural': '- Threads Ended',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('chronicles.thread',),
        ),
    ]