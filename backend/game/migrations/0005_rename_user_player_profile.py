# Generated by Django 5.1.2 on 2024-12-16 17:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0004_alter_player_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='player',
            old_name='user',
            new_name='profile',
        ),
    ]