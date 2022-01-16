# Generated by Django 3.2.8 on 2022-01-16 21:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rules', '0002_remove_weapontype_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='SkillType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kind', models.CharField(choices=[('Powszechne', 'Powszechne'), ('Kapłańskie', 'Kapłańskie'), ('Magiczne', 'Magiczne')], default='Powszechne', max_length=100)),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
            options={
                'ordering': ['kind', 'name'],
            },
        ),
        migrations.AddField(
            model_name='skill',
            name='types',
            field=models.ManyToManyField(blank=True, related_name='skills', to='rules.SkillType'),
        ),
    ]