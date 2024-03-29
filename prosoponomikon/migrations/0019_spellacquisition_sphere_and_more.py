# Generated by Django 4.1.7 on 2023-05-28 11:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rules', '0010_delete_sphragis_delete_priestsskill_and_more'),
        ('prosoponomikon', '0018_alter_acquisition_unique_together_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='spellacquisition',
            name='sphere',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='rules.sphere'),
        ),
        migrations.AlterField(
            model_name='spellacquisition',
            name='sphragis',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='rules.domain'),
        ),
    ]
