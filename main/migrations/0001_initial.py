# Generated by Django 5.0.6 on 2025-03-25 00:51

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Customisations",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("customisation_type", models.IntegerField()),
                ("primary_colour_code", models.TextField()),
                ("secondary_colour_code", models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name="Plant",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("requirement_type", models.IntegerField()),
                ("rarity", models.IntegerField()),
                ("plant_name", models.TextField(default="plant")),
            ],
        ),
        migrations.CreateModel(
            name="UserForest",
            fields=[
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        serialize=False,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "cells",
                    models.TextField(
                        default="0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0"
                    ),
                ),
                (
                    "last_growth_check_date",
                    models.TextField(default="<class 'datetime.date'>"),
                ),
                ("customisations", models.TextField(default="0,1,2")),
            ],
        ),
        migrations.CreateModel(
            name="UserHighScore",
            fields=[
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        serialize=False,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                ("high_score", models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name="UserInventory",
            fields=[
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        serialize=False,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                ("paper", models.IntegerField(default=0)),
                ("plastic", models.IntegerField(default=0)),
                ("compost", models.IntegerField(default=0)),
                ("recycled_paper", models.IntegerField(default=0)),
                ("recycled_plastic", models.IntegerField(default=0)),
                ("recycled_compost", models.IntegerField(default=0)),
                ("tree_guard", models.IntegerField(default=0)),
                ("rain_catcher", models.IntegerField(default=0)),
                ("fertilizer", models.IntegerField(default=0)),
                ("oak", models.IntegerField(default=0)),
                ("birch", models.IntegerField(default=0)),
                ("fir", models.IntegerField(default=0)),
                ("red_campion", models.IntegerField(default=0)),
                ("poppy", models.IntegerField(default=0)),
                ("cotoneaster", models.IntegerField(default=0)),
                ("collected_markers", models.TextField(default="")),
                ("last_collected", models.TextField(default="<class 'datetime.date'>")),
            ],
        ),
    ]
