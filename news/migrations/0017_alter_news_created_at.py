# Generated by Django 3.2.8 on 2022-01-06 12:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0016_alter_news_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='news',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
