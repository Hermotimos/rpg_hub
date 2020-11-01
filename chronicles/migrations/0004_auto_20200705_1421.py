# Generated by Django 2.2.1 on 2020-07-05 12:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chronicles', '0003_auto_20200705_0722'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='timeunit',
            options={'ordering': ['year_start_ab_urbe_condita', 'date_start'], 'verbose_name_plural': 'Time Units (Time spans, History events, Game events)'},
        ),
        migrations.AlterField(
            model_name='date',
            name='season',
            field=models.CharField(blank=True, choices=[('Wiosny', 'Wiosny'), ('Lata', 'Lata'), ('Jesieni', 'Jesieni'), ('Zimy', 'Zimy')], max_length=6, null=True),
        ),
        migrations.AlterField(
            model_name='timeunit',
            name='game',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='events', to='chronicles.GameSession'),
        ),
    ]