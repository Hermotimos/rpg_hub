# Generated by Django 3.1 on 2021-01-06 16:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_auto_20210106_1613'),
        ('news', '0002_auto_20201225_1400'),
    ]

    operations = [
        migrations.AddField(
            model_name='news',
            name='author2',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='news_authored', to='users.profile'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='newsanswer',
            name='author2',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='news_answers', to='users.profile'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='survey',
            name='author2',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='surveys_authored', to='users.profile'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='surveyanswer',
            name='author2',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='survey_answers', to='users.profile'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='surveyoption',
            name='author2',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='survey_options_authored', to='users.profile'),
            preserve_default=False,
        ),
    ]
