# Generated by Django 5.1.6 on 2025-02-26 19:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('announcements', '0003_announcement_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='announcement',
            name='summary',
            field=models.TextField(max_length=200),
        ),
    ]
