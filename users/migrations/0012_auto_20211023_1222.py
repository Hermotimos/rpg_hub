# Generated by Django 3.1 on 2021-10-23 10:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_auto_20211023_1146'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='profile',
            options={'ordering': ['-status', '-is_active', 'user_fk__username']},
        ),
        migrations.RemoveField(
            model_name='profile',
            name='user',
        ),
    ]