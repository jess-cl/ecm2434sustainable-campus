from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.shop_items, name='shop'),
    path('buy/<int:item_id>/', views.buy_shop_item, name='buy_shop_item'),
    path('display_redeem_code/<str:redeem_code>/', views.display_redeem_qr_code, name='display_redeem_code'),
    path('redeem_page/', views.redeem_page, name='redeem_page'),
    path('redeem_item/<str:redeem_code>/', views.redeem_item, name='redeem_item'),
    path('redeemed/', views.redeemed, name='redeemed'),
    path('purchased_items/', views.purchased_items, name='purchased_items'),
    path('already_redeemed/', views.already_redeemed, name='already_redeemed'),
    path('unauthorised/', views.unauthorised, name='unauthorised'),
    path('transactions/', views.transactions, name='transactions'),
]