# Generated by Django 3.1 on 2020-09-26 16:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20200926_1248'),
        ('development', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profileklass',
            name='profile',
        ),
        migrations.AddField(
            model_name='profileklass',
            name='profile',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='profile_klasses', to='users.profile'),
            preserve_default=False,
        ),
    ]
