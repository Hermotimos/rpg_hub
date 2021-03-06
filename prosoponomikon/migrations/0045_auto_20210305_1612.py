# Generated by Django 3.1 on 2021-03-05 15:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prosoponomikon', '0044_auto_20210305_1513'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='auxiliarynamegroup',
            options={'ordering': ['location', 'social_info']},
        ),
        migrations.AlterModelOptions(
            name='namegroup',
            options={'ordering': ['title']},
        ),
        migrations.AlterField(
            model_name='affixgroup',
            name='type',
            field=models.CharField(choices=[('MALE', 'MALE'), ('FEMALE', 'FEMALE')], default='male', max_length=20),
        ),
        migrations.AlterUniqueTogether(
            name='affixgroup',
            unique_together={('affix', 'name_group')},
        ),
    ]
