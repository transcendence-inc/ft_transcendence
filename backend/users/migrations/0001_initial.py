# Generated by Django 5.1.6 on 2025-02-05 20:07

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('game', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Friends',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('accepted', models.BooleanField(default=False)),
                ('origin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('target', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='target_for_friends', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(default='default.jpg', upload_to='profile_pics')),
                ('online', models.BooleanField(default=False)),
                ('quiz_games_played', models.IntegerField(default=0)),
                ('quiz_games_won', models.IntegerField(default=0)),
                ('quiz_total_score', models.BigIntegerField(default=0)),
                ('quiz_high_score', models.IntegerField(default=0)),
                ('quiz_questions_asked', models.IntegerField(default=0)),
                ('quiz_correct_answers', models.IntegerField(default=0)),
                ('pong_games_won', models.IntegerField(default=0)),
                ('pong_games_lost', models.IntegerField(default=0)),
                ('player', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='profile_player', to='game.player')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
