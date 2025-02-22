from django.contrib import admin
from .models import UserBalance, CurrencyTransaction, ShopItem, ItemPurchase

# Adds UserBalance sql table to Django admin
class UserBalanceAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'currency')  
    search_fields = ('user_id__username',)  

# Adds CurrencyTransaction sql table to Django admin
class CurrencyTransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'user', 'currency_difference', 'transaction_datetime', 'game_keeper')
    search_fields = ('user__username', 'game_keeper__username')

# Adds ShopItem sql table to Django admin
class ShopItemAdmin(admin.ModelAdmin):
    list_display = ('item_id', 'name', 'currency_cost', 'is_digital', 'description')  
    search_fields = ('name', 'description')  

# Adds ItemPurchase sql table to Django admin
class ItemPurchaseAdmin(admin.ModelAdmin):
    list_display = ('purchase_id', 'user', 'item', 'purchase_date_time', 'is_digital', 'redeem_code', 'is_redeemed')
    search_fields = ('user__username', 'item__name', 'redeem_code') 

admin.site.register(UserBalance, UserBalanceAdmin)
admin.site.register(CurrencyTransaction, CurrencyTransactionAdmin)
admin.site.register(ShopItem, ShopItemAdmin)
admin.site.register(ItemPurchase, ItemPurchaseAdmin)
