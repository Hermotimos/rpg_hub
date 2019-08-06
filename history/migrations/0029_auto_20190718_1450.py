# Generated by Django 2.2.1 on 2019-07-18 12:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0028_auto_20190718_1431'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventnote',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notes', to=settings.AUTH_USER_MODEL),
        ),
    ]
