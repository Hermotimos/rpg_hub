# Generated by Django 4.0.4 on 2022-08-20 09:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0002_itemcollection_item_collection'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='type',
            field=models.CharField(blank=True, choices=[('Osobisty', 'Osobisty'), ('Bagaż', 'Bagaż'), ('Depozyt', 'Depozyt'), ('Skrytka', 'Skrytka'), ('Koń/Muł', 'Koń/Muł'), ('Tragarz', 'Tragarz')], max_length=255, null=True),
        ),
    ]
