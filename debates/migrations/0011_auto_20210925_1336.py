# Generated by Django 3.1 on 2021-09-25 11:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('debates', '0010_auto_20210220_1110'),
    ]

    operations = [
        migrations.RenameField(
            model_name='debate',
            old_name='name',
            new_name='title',
        ),
    ]
