# Generated by Django 5.1.5 on 2025-02-24 14:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('announcements', '0002_announcement_summary'),
    ]

    operations = [
        migrations.AddField(
            model_name='announcement',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='announcement_images/'),
        ),
    ]
