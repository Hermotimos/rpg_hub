# Generated by Django 3.1 on 2021-09-25 15:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_auto_20210912_1017'),
        ('news', '0007_auto_20210925_1623'),
    ]

    operations = [
        migrations.AlterField(
            model_name='news',
            name='allowed_profiles',
            field=models.ManyToManyField(related_name='allowed_news', to='users.Profile', verbose_name='Adresaci ogłoszenia'),
        ),
    ]