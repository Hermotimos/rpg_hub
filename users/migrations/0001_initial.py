# Generated by Django 4.0.4 on 2022-07-10 12:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, default='profile_pics/profile_default.jpg', null=True, upload_to='profile_pics')),
                ('status', models.CharField(choices=[('gm', 'MG'), ('npc', 'BN'), ('player', 'GRACZ'), ('spectator', 'WIDZ')], default='npc', max_length=50)),
                ('is_active', models.BooleanField(default=True)),
                ('is_alive', models.BooleanField(default=True)),
                ('user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='profiles', to=settings.AUTH_USER_MODEL)),
                ('user_image', models.ImageField(blank=True, default='profile_pics/profile_default.jpg', null=True, upload_to='user_pics')),
            ],
            options={
                'ordering': ['-status', '-is_active', 'character__fullname'],
            },
        ),
    ]
