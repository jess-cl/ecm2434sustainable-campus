# Generated by Django 5.1.6 on 2025-02-23 16:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('leaderboards', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='treescore',
            old_name='user_id',
            new_name='user',
        ),
    ]
