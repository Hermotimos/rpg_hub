# Generated by Django 4.0.4 on 2022-05-26 20:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('imaginarion', '0003_alter_picture_options_alter_pictureimage_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pictureimage',
            name='image',
            field=models.ImageField(upload_to='post_pics'),
        ),
    ]
