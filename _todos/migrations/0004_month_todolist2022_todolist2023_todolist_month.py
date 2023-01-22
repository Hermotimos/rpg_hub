# Generated by Django 4.0.4 on 2023-01-22 21:35

import _todos.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('_todos', '0003_alter_todolist_noa'),
    ]

    operations = [
        migrations.CreateModel(
            name='Month',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('monthdate', models.DateField(default=_todos.models.monthdate, unique=True)),
            ],
            options={
                'ordering': ['-monthdate'],
            },
        ),
        migrations.CreateModel(
            name='TODOList2022',
            fields=[
            ],
            options={
                'verbose_name': 'TODO 2022',
                'verbose_name_plural': 'TODOs 2022',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('_todos.todolist',),
        ),
        migrations.CreateModel(
            name='TODOList2023',
            fields=[
            ],
            options={
                'verbose_name': 'TODO 2023',
                'verbose_name_plural': 'TODOs 2023',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('_todos.todolist',),
        ),
        migrations.AddField(
            model_name='todolist',
            name='month',
            field=models.ForeignKey(default=_todos.models.thismonth, on_delete=django.db.models.deletion.PROTECT, related_name='days', to='_todos.month'),
        ),
    ]
