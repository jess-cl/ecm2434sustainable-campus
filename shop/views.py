import string, random, qrcode, os
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from .models import ShopItem, UserBalance, ItemPurchase, CurrencyTransaction
from accounts.models import CustomUser

# View for shop_items.html page. Displays buyable items, and sends buy requests to buy_shop_item view
@login_required 
def shop_items(request):
    """Retrieves and displays all shop items. Also retrieves and displays user's balance"""

    # Retrieves all items stored in the ShopItem table
    items = ShopItem.objects.all()

    # Ensures gamekeepers and developers dont need balances created in the database 
    if request.user.role == "player":
        user_balance = UserBalance.objects.get(user_id=request.user)
    else: 
        user_balance = None

    context = {'items':items, 'user_balance':user_balance}
    return render(request, 'shop/shop.html', context)

@login_required
def add_shop_item(request):
    """Allows game keeper or developer to add new items. This view creates new shop items using the data
       submitted on the add_shop_item.html page."""
    
    # Verifies user is a gamekeeper or developer
    if request.user.role == 'player':
        messages.error(request, "You do not have permission to add new items.")
        return redirect('shop:shop')

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        currency_cost = request.POST.get('currency_cost')
        is_digital = 'is_digital' in request.POST 
        image = request.FILES.get('image')

        if not name or not description or not currency_cost or not image:
            messages.error(request, "All fields must be filled out before submitting.")
            return render(request, 'shop/add_shop_item.html')

        # Create and save the new item
        item = ShopItem(
            name=name,
            description=description,
            currency_cost=currency_cost,
            is_digital=is_digital,
            image=image
        )
        item.save()

        messages.success(request, "New item has been added to the shop!")
        return redirect('shop:shop')

    return render(request, 'shop/add_shop_item.html')

@login_required
def remove_shop_item(request, item_id):
    """Allows game keepers and developers to remove shop items from store. Items not already redeemed
       by player that are removed from store are refunded."""

    # Verifies user is a gamekeeper or developer
    if request.user.role == 'player':
        messages.error(request, "You do not have permission to remove items.")
        return redirect('shop:shop')

    try:
        # Retrieve the item
        item = ShopItem.objects.get(item_id=item_id)
    except ShopItem.DoesNotExist:
        # Returns an error message if item id does not match any item
        messages.error(request, "Item not found.")
        return redirect('shop:shop')

    item_purchases = ItemPurchase.objects.filter(item=item)

    for purchase in item_purchases:
        if purchase.is_redeemed == False:
            user_balance = UserBalance.objects.get(user_id=purchase.user)

            # Refund the user by adding the currency cost of the item back into the player's balance
            user_balance.currency += item.currency_cost
            user_balance.save()

            # Create a refund transaction record
            CurrencyTransaction.objects.create(
                user=purchase.user,
                currency_difference=item.currency_cost,
                description=f"Refund for {item.name} removal"
            )

    item.delete()  # Remove the item from the database
    messages.success(request, f"The item '{item.name}' has been removed from the shop.")
    
    return redirect('shop:shop')


@login_required 
def buy_shop_item(request, item_id):
    """Allows players to buy items from the item shop."""

    # Verifies user is a player
    if request.user.role != "player":
        messages.error(request, "You must be a Player to buy items.")
        return redirect('shop:shop')

    try:
        # Retrieve the item
        item = ShopItem.objects.get(item_id=item_id)
    except ShopItem.DoesNotExist:
        # Returns an error message if item id does not match any item
        messages.error(request, "Item not found.")
        return redirect('shop:shop_items')  # Redirect back to the shop page or some other page
    
    user_balance = UserBalance.objects.get(user_id=request.user)

    # Checks if user has enough currency to buy the item
    if user_balance.currency >= item.currency_cost:
        # Removes item cost from user balance, and saves balance
        user_balance.currency -= item.currency_cost
        user_balance.save()

        # Stores transaction in db 
        CurrencyTransaction.objects.create(
            user=request.user, 
            currency_difference=-item.currency_cost, 
            description=f"Bought {item.name}"
        )

        # If item isn't digital, stores a randomly generated 6 figure code in item purchase
        if not item.is_digital:
            redeem_code = redeem_code_generator()
            ItemPurchase.objects.create(
                user=request.user, 
                item=item, 
                is_digital=False, 
                redeem_code=redeem_code
            ) 

        else:
            ItemPurchase.objects.create(
                user=request.user, 
                item=item, 
                is_digital=True
            ) 

        messages.success(request, f"You successfully bought {item.name}.")

    else:
        messages.error(request, "You do not have enough currency.")

    return redirect('/shop/')


def redeem_code_generator(size=6, chars=string.ascii_uppercase + string.digits):
    """Helper function used for generating a random, and unique 6 figure redeem code"""
    while True:
        redeem_code = ''.join(random.choice(chars) for _ in range(size))
        if ItemPurchase.objects.filter(redeem_code=redeem_code).exists() == False:
            return redeem_code


@login_required 
def purchased_items(request):
    """Retrieves and displays all purchases made by logged in user."""
    purchases = ItemPurchase.objects.filter(user=request.user)
    context = {'purchases':purchases}
    return render(request, 'shop/purchased_items.html', context)

@login_required 
def display_redeem_qr_code(request, redeem_code):
    """Allows player to display the redeem QR code of a purchase, to allow a gamekeeper or developer
       to scan to redeem it."""
    # Verifies user is a player
    if request.user.role != "player":
        messages.error(request, "You must be a Player to access this page.")
        return redirect('shop:shop')

    try:
        # Retrieve the item purchase
        purchase = ItemPurchase.objects.get(redeem_code=redeem_code)
    except ItemPurchase.DoesNotExist:
        # If item purchase does not exist, the user is redirected, and given an error message
        messages.error(request, "Item purchase not found.")
        return redirect('shop:purchased_items')

    # Ensures the qr code is only displayed to the buyer of item
    if request.user != purchase.user:
        messages.error(request, "You can not redeem an item purchase that is not yours.")
        return redirect('shop:purchased_items')

    # If item is already redeemed, redirects user to a different page to inform them
    if purchase.is_redeemed == True:
        messages.error(request, "You have already redeemed this item.")
        return redirect('shop:purchased_items')

    # Generates QR code for redeeming item
    redeem_url = request.build_absolute_uri(reverse('shop:redeem_item', args=[redeem_code]))
    qr_code = qrcode.make(redeem_url)

    # Creates qr_code image using url, and saves it in media/qr_codes
    qr_code_folderpath = os.path.join(settings.MEDIA_ROOT, 'qr_codes/')
    qr_code_name = f"{redeem_code}.jpg"
    qr_code_filepath = os.path.join(qr_code_folderpath + qr_code_name)
    qr_code.save(qr_code_filepath)

    # Sends the location of qr_code and purchase to html page
    qr_code_url = f"{settings.MEDIA_URL}qr_codes/{qr_code_name}"
    context = {'qr_code':qr_code_url, 'purchase':purchase}

    return render(request, 'shop/display_redeem_code.html', context)

@login_required 
def redeem_page(request):
    """Allows game keepers and developers to redeem player purchases by inputting the 6 figure code 
       into this views input. """

    # Verifies user has permissions
    if request.user.role == "player":
        messages.error(request, "You must be a Game Keeper or Developer to access this page.")
        return redirect('shop:shop')
    
    # Retrieves given redeem code, and checks if it matches a purchase. If so, sends user to redeem_item.html page
    if request.method == 'POST':
        redeem_code = request.POST.get('redeem_code')
        purchase = ItemPurchase.objects.filter(redeem_code=redeem_code).first()

        if purchase: 
            if purchase.is_redeemed: # Ensures item isnt already redeemed
                messages.error(request, "This item has already been redeemed.")
                return redirect('shop:redeem_page')
            else: 
                return redirect('shop:redeem_item', redeem_code=redeem_code)
        else: 
            messages.error(request, 'Invalid redeem code, please try again.')

    return render(request, 'shop/redeem_page.html')


@login_required 
def redeem_item(request, redeem_code):
    """Allows game keeper or developer to redeem player item. Page is accessed through either redeem code, 
       or scanning QR code attached to player purchase."""
    
    # Verifies user is a game keeper, or developer
    if request.user.role == "player":
        messages.error(request, "You must be a Game Keeper or Developer to access this page.")
        return redirect('shop:shop')

    try:
        purchase = ItemPurchase.objects.get(redeem_code=redeem_code)
    except ItemPurchase.DoesNotExist:
        # Returns error if item purchase does not exist
        messages.error(request, "Item purchase does not exist")
        return redirect('shop:purchased_items')
    
    # Redeems item if button on html is pressed.
    if request.method == 'POST':
        purchase.is_redeemed = True
        purchase.save()

        messages.success(request, "Player item has successfully been redeemed.")
        return redirect('shop:redeem_page')

    context = {'purchase': purchase}
    return render(request, 'shop/redeem_item.html', context)

@login_required
def refund_item(request, purchase_id):
    """Allows players to refund item purchases they own."""
    
    # Retrieve the purchase if it exists. Ensures only buyer can refund item purchase
    try:
        purchase = ItemPurchase.objects.get(purchase_id=purchase_id, user=request.user)
    except ItemPurchase.DoesNotExist:
        # Returns error if item purchase does not exist, or user isn't the buyer
        messages.error(request, "Cannot refund purchase, as you are not the buyer, or it does not exist.")
        return redirect('shop:purchased_items')

    # Verifies item is non-digital
    if purchase.is_digital == True:
        messages.error(request, "Digital items cannot be refunded.")
        return redirect('shop:purchased_items')

    # Verifies item is unredeemed
    if purchase.is_redeemed == True:
        messages.error(request, "This item has already been redeemed and cannot be refunded.")
        return redirect('shop:purchased_items')

    # Get the user's balance and add back the currency
    user_balance = UserBalance.objects.get(user_id=request.user)
    user_balance.currency += purchase.item.currency_cost
    user_balance.save()

    # Record the refund transaction
    CurrencyTransaction.objects.create(
        user=request.user,
        currency_difference=purchase.item.currency_cost,
        description=f"Refunded {purchase.item.name}"
    )

    # Delete the refunded purchase
    purchase.delete()

    messages.success(request, f"You have successfully refunded {purchase.item.name} and received {purchase.item.currency_cost} currency.")
    
    return redirect('shop:purchased_items')

@login_required
def transaction_history(request, user_id):
    """Allows players to view all transactions done on their account. It also allows game keepers and 
       developers to view the transactions of a specified player."""
    
    try:
        # Retrieves user 
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        # Returns error user does not exist
        messages.error(request, "Cannot display transactions of specified player as the given ID isnt associated with any account.")
        return redirect('main:map')

    # Check if the logged-in user is either the owner or a gamekeeper
    if request.user != user and request.user.role == 'player':
        messages.error(request, "You do not have permissions to view the transactions of specified player.")
        return redirect('main:map')
    
    # Ensures only players can have their transactions viewed
    if user.role != "player":
        messages.error(request, "Gamekeepers and developers do not have transactions to view.")
        return redirect('main:map')

    # Retrieve transactions for the player, sorted from newest to oldest
    transactions = CurrencyTransaction.objects.filter(user=user).order_by('-transaction_datetime')

    return render(request, 'shop/transaction_history.html', {'transactions': transactions, 'user': user})