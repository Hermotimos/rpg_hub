# Generated by Django 3.2.8 on 2021-11-13 12:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0013_auto_20211023_1358'),
        ('communications', '0005_auto_20211026_2032'),
    ]

    operations = [
        migrations.CreateModel(
            name='ThreadTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=30)),
                ('color', models.CharField(default='#FFFFFF', max_length=7)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='thread_tags', to='users.profile')),
            ],
            options={
                'ordering': ['title'],
            },
        ),
        migrations.AddField(
            model_name='thread',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='threads', to='communications.ThreadTag'),
        ),
    ]
