# Generated by Django 3.1 on 2021-01-06 16:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_auto_20210106_1613'),
        ('debates', '0004_auto_20201230_2219'),
    ]

    operations = [
        migrations.AddField(
            model_name='remark',
            name='author2',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='remarks', to='users.profile', verbose_name='Autor'),
            preserve_default=False,
        ),
    ]
