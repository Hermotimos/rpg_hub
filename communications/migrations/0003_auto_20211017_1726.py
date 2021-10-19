# Generated by Django 3.1 on 2021-10-17 15:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_auto_20210912_1017'),
        ('communications', '0002_auto_20211017_1710'),
    ]

    operations = [
        migrations.CreateModel(
            name='SurveyOption',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=50)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='survey_options', to='users.profile')),
                ('voters_no', models.ManyToManyField(blank=True, related_name='survey_options_no', to='users.Profile')),
                ('voters_yes', models.ManyToManyField(blank=True, related_name='survey_options_yes', to='users.Profile')),
            ],
            options={
                'ordering': ['text'],
            },
        ),
        migrations.AddField(
            model_name='statement',
            name='survey_options',
            field=models.ManyToManyField(blank=True, related_name='threads', to='communications.SurveyOption'),
        ),
    ]