# Generated by Django 3.1 on 2021-03-05 12:25

from django.db import migrations


class Migration(migrations.Migration):
    atomic = False
    
    dependencies = [
        ('toponomikon', '0003_auto_20210106_1613'),
        ('prosoponomikon', '0039_auto_20210305_1323'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='NameForm',
            new_name='Name',
        ),
    ]