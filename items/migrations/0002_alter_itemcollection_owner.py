# Generated by Django 4.1.4 on 2023-02-14 21:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('prosoponomikon', '0013_rename_weapon_acquisition_weapon_type_and_more'),
        ('items', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='itemcollection',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='collections', to='prosoponomikon.character'),
        ),
    ]
