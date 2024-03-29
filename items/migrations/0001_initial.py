# Generated by Django 4.0.4 on 2022-08-20 11:50

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('prosoponomikon', '0005_acquaintanceship_knows_as_description_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ItemCollection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='collections', to='prosoponomikon.character')),
            ],
            options={
                'ordering': ['owner__fullname', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('info', models.TextField(blank=True, null=True)),
                ('weight', models.DecimalField(decimal_places=2, default=0, max_digits=12, validators=[django.core.validators.MinValueValidator(0)])),
                ('is_deleted', models.BooleanField(default=False)),
                ('collection', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='items', to='items.itemcollection')),
            ],
            options={
                'ordering': ['collection', 'name'],
            },
        ),
    ]
