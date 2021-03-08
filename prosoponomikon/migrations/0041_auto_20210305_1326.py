# Generated by Django 3.1 on 2021-03-05 12:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('prosoponomikon', '0040_auto_20210305_1325'),
    ]

    operations = [
        migrations.AlterField(
            model_name='character',
            name='name',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='characters', to='prosoponomikon.name'),
        ),
    ]