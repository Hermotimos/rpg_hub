# Generated by Django 3.1 on 2021-01-06 16:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0004_auto_20210106_1710'),
    ]

    operations = [
        migrations.RenameField(
            model_name='news',
            old_name='author2',
            new_name='author',
        ),
        migrations.RenameField(
            model_name='newsanswer',
            old_name='author2',
            new_name='author',
        ),
        migrations.RenameField(
            model_name='survey',
            old_name='author2',
            new_name='author',
        ),
        migrations.RenameField(
            model_name='surveyanswer',
            old_name='author2',
            new_name='author',
        ),
        migrations.RenameField(
            model_name='surveyoption',
            old_name='author2',
            new_name='author',
        ),
    ]