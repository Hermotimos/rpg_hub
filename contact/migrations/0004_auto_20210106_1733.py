# Generated by Django 3.1 on 2021-01-06 16:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_auto_20210106_1613'),
        ('contact', '0003_auto_20201228_2101'),
    ]

    operations = [
        migrations.AddField(
            model_name='demand',
            name='addressee2',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='received_demands', to='users.profile', verbose_name='Adresat'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='demand',
            name='author2',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='authored_demands', to='users.profile'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='demandanswer',
            name='author2',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='demand_answers', to='users.profile'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='plan',
            name='author2',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='plans', to='users.profile'),
            preserve_default=False,
        ),
    ]
