# Generated by Django 5.1.5 on 2025-02-05 04:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0005_tournement_playernum'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tournement',
            name='playernum',
            field=models.IntegerField(default=1),
        ),
    ]
