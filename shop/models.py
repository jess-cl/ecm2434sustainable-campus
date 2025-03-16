from django.db import models

class UserBalance(models.Model):
    """Represents a user's balance"""
    user_id = models.OneToOneField('accounts.CustomUser', on_delete=models.CASCADE, primary_key=True)
    currency = models.IntegerField(default=0) 

class CurrencyTransaction(models.Model):
    """Records when users earns or spends currency"""
    transaction_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='currency_transactions')
    currency_difference = models.IntegerField()  # Positive for receiving, and negative for spending
    description = models.TextField()
    transaction_datetime = models.DateTimeField(auto_now_add=True)
    game_keeper = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True, blank=True, related_name='currency_rewarded')

class ShopItem(models.Model):
    """Represents an item in the shop a user can buy using currency"""
    item_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    currency_cost = models.PositiveIntegerField(default=1)
    image = models.ImageField(upload_to="shop_items/", null=True, blank=True)
    is_digital = models.BooleanField(default=True)

class ItemPurchase(models.Model):
    """Represents a purchase made by a user"""
    purchase_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
    item = models.ForeignKey(ShopItem, on_delete=models.CASCADE)
    purchase_date_time = models.DateTimeField(auto_now_add=True)
    is_digital = models.BooleanField(default=True)
    redeem_code = models.CharField(max_length=6, unique=True, blank=True, null=True, default=None)
    is_redeemed = models.BooleanField(default=False)
