# Generated by Django 5.1.5 on 2025-02-24 14:30

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('announcements', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='announcement',
            name='summary',
            field=models.TextField(),
            preserve_default=False,
        ),
    ]