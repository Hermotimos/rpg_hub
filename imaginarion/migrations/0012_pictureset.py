# Generated by Django 3.1 on 2021-03-12 11:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('imaginarion', '0011_auto_20210221_1423'),
    ]

    operations = [
        migrations.CreateModel(
            name='PictureSet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('pictures', models.ManyToManyField(blank=True, related_name='picture_sets', to='imaginarion.Picture')),
            ],
            options={
                'ordering': ['title'],
            },
        ),
    ]
