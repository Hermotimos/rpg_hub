# Generated by Django 3.1 on 2021-01-03 05:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20201225_1757'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='image',
            field=models.ImageField(blank=True, default='profile_pics/profile_default.jpg', null=True, upload_to='profile_pics'),
        ),
    ]
