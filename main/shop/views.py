from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from .models import ShopItem, UserBalance, ItemPurchase, CurrencyTransaction
import string, random
from django.conf import settings
import os

# Create your views here.

# View for shop_items.html page. Displays buyable items, and sends buy requests to buy_shop_item view
def shop_items(request):
    # When user presses buy on an item, this handles the purchase.
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        return redirect(f'/shop/buy/{item_id}')

    # Retrieves all items stored in the ShopItem table
    items = ShopItem.objects.filter()

    user_balance = UserBalance.objects.get(user_id=request.user)
    context = {'items':items, 'user_balance':user_balance}

    return render(request, 'shop/shop.html', context)

# View used for handling purchase of an item
def buy_shop_item(request, item_id):
    # retrieves item, and buyer's balance
    item = ShopItem.objects.get(item_id=item_id)
    user_balance = UserBalance.objects.get(user_id=request.user)

    # Checks if user has enough currency to buy the item
    if user_balance.currency >= item.currency_cost:
        # Removes item cost from user balance, and saves balance
        user_balance.currency = user_balance.currency - item.currency_cost
        user_balance.save()

        # Stores transaction in db 
        CurrencyTransaction.objects.create(user=request.user, currency_difference=-item.currency_cost, description=f"Bought {item.name}")

        # If item isn't digital, stores a randomly generated 6 figure code in item purchase
        if item.is_digital == False:
            redeem_code = redeem_code_generator()
            ItemPurchase.objects.create(user=request.user, item=item, is_digital=False, redeem_code=redeem_code) 

        else:
            ItemPurchase.objects.create(user=request.user, item=item, is_digital=True) 

        messages.success(request, f"You successfully bought {item.name}.")

    else:
        messages.error(request, "You do not have enough currency.")

    return redirect('/shop/')

# Function used for generating 6 figure redeem code. 
def redeem_code_generator(size=6, chars=string.ascii_uppercase + string.digits):
    while True:
        redeem_code = ''.join(random.choice(chars) for _ in range(size))
        if ItemPurchase.objects.filter(redeem_code=redeem_code).exists() == False:
            return redeem_code

# View for purchased_items.html. Retrieves all purchases made by user, and sends it to html
def purchased_items(request):
    purchases = ItemPurchase.objects.filter(user=request.user)
    context = {'purchases':purchases}
    return render(request, 'shop/purchased_items.html', context)

# View for display_redeem_code.html. Used to generate QR code for redeeming items by game keepers. 
def display_redeem_qr_code(request, redeem_code):
    purchase = get_object_or_404(ItemPurchase, redeem_code=redeem_code)

    # Ensures the qr code is only displayed to the buyer of item
    if request.user != purchase.user:
        return redirect('shop:unauthorised')

    # If item is already redeemed, redirects user to a different page to inform them
    if purchase.is_redeemed == True:
        return redirect('shop:already_redeemed')

    # Generates url for redeeming item
    redeem_url = request.build_absolute_uri(reverse('shop:redeem_item', args=[redeem_code]))

    # Creates qr_code image using url, and saves it in media/qr_codes
    qr_code = qrcode.make(redeem_url)
    qr_code_folderpath = os.path.join(settings.MEDIA_ROOT, 'qr_codes/')
    qr_code_name = f"{redeem_code}.jpg"
    qr_code_filepath = os.path.join(qr_code_folderpath + qr_code_name)
    qr_code.save(qr_code_filepath)

    # Sends the location of qr_code and purchase to html page
    qr_code_url = f"{settings.MEDIA_URL}qr_codes/{qr_code_name}"
    context = {'qr_code':qr_code_url, 'purchase':purchase}

    return render(request, 'shop/display_redeem_code.html', context)

# View for redeem_page.html. Used by game keepers to input redeem codes.
def redeem_page(request):
    # Ensures user has permissions
    if request.user.is_staff == False:
        return redirect('shop:unauthorised')
    
    # Retrieves given redeem code, and checks if it matches a purchase. If so, sends user to redeem_item.html page
    if request.method == 'POST':
        redeem_code = request.POST.get('redeem_code')

        purchase = ItemPurchase.objects.filter(redeem_code=redeem_code)

        if purchase.exists():
            return redirect('shop:redeem_item', redeem_code=redeem_code)
        else: 
            messages.error(request, 'Invalid redeem code, please try again.')

    return render(request, 'shop/redeem_page.html')


# View for redeem_item.html. Used for redeeming items. 
def redeem_item(request, redeem_code):
    # Ensures user has permissions
    if request.user.is_staff == False:
        return render(request, 'shop/unauthorised.html')

    # Retrieves purchase if it exists
    purchase = get_object_or_404(ItemPurchase, redeem_code=redeem_code)
    
    # Redeems item if button on html is pressed. Sends user to redeem.html page after
    if request.method == 'POST':
        purchase.is_redeemed = True
        purchase.save()
        return redirect('shop:redeemed')

    context = {'purchase': purchase}
    return render(request, 'shop/redeem_item.html', context)

# View for redeem.html. Used for showing success in redeeming an item by a game keeper
def redeemed(request): 
    return render(request, 'shop/redeemed.html')

# View for already_redeem.html. Used for informing user that item already been redeemed
def already_redeemed(request): 
    return render(request, 'shop/already_redeemed.html')

# View for unauthorised.html. Used for informing user that they are unauthorised
def unauthorised(request):
    return render(request, 'shop/unauthorised.html')


def transactions(request):
    return render(request, 'transactions.html')

