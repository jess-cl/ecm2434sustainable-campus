# Generated by Django 5.0.6 on 2025-03-25 00:49

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("accounts", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ShopItem",
            fields=[
                ("item_id", models.AutoField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=100, unique=True)),
                ("description", models.TextField(blank=True)),
                ("currency_cost", models.PositiveIntegerField(default=1)),
                (
                    "image",
                    models.ImageField(blank=True, null=True, upload_to="shop_items/"),
                ),
                ("is_digital", models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name="UserBalance",
            fields=[
                (
                    "user_id",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        serialize=False,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                ("currency", models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name="CurrencyTransaction",
            fields=[
                ("transaction_id", models.AutoField(primary_key=True, serialize=False)),
                ("currency_difference", models.IntegerField()),
                ("description", models.TextField()),
                ("transaction_datetime", models.DateTimeField(auto_now_add=True)),
                (
                    "game_keeper",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="currency_rewarded",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="currency_transactions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ItemPurchase",
            fields=[
                ("purchase_id", models.AutoField(primary_key=True, serialize=False)),
                ("purchase_date_time", models.DateTimeField(auto_now_add=True)),
                ("is_digital", models.BooleanField(default=True)),
                (
                    "redeem_code",
                    models.CharField(
                        blank=True, default=None, max_length=6, null=True, unique=True
                    ),
                ),
                ("is_redeemed", models.BooleanField(default=False)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "item",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="shop.shopitem"
                    ),
                ),
            ],
        ),
    ]
