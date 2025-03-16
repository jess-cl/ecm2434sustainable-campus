from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from accounts.models import CustomUser
from .models import ShopItem, UserBalance, CurrencyTransaction, ItemPurchase
import os
import glob
from django.conf import settings
from django.test import override_settings
import tempfile

# Setup many of the 
@override_settings(MEDIA_ROOT=tempfile.mkdtemp()) # Makes temporary media folder for storage of test images 
class SetUpTest(TestCase):
    def setUp(self):
        self.shop_url=reverse('shop:shop')
        self.redeem_page_url = reverse('shop:redeem_page')
        self.purchased_items_url = reverse('shop:purchased_items')


        # Creates a test player account
        self.player = CustomUser.objects.create_user(email ='player@gmail.com', 
                                                    username = 'player1', 
                                                    password = 'testpassword12345',
                                                    first_name = 'Player',
                                                    last_name = 'User',
                                                    role = 'player',
                                                    verified = True)
        # Creates initial balance for test player
        self.player_balance = UserBalance.objects.create(user_id = self.player, currency = 20)

        # Fake image used for shop items
        self.test_image = SimpleUploadedFile(
            name = 'test_image.jpg',
            content = b'',
            content_type = 'image/jpeg'
        )

        # Creates digital shop item
        self.digital_shop_item = ShopItem.objects.create(name="Digital item", currency_cost=10, 
                                                         description = 'digital item description',
                                                         image = self.test_image, is_digital=True)
        
        # URL to buy above item
        self.buy_digital_item_url=(reverse('shop:buy_shop_item', args=[self.digital_shop_item.item_id]))
        
        # Creates non-digital shop item
        self.non_digital_shop_item = ShopItem.objects.create(name="Non Digital item", currency_cost=10, 
                                                             description = 'non-digital item description',
                                                             image = self.test_image, is_digital=False)
        
        # URL to buy above item
        self.buy_non_digital_item_url=(reverse('shop:buy_shop_item', args=[self.non_digital_shop_item.item_id]))

        # URL to redeem non-digital shop item
        self.redeem_non_digital_item_url=(reverse('shop:buy_shop_item', args=[self.non_digital_shop_item.item_id]))

        # Creates a test game keeper account
        self.game_keeper = CustomUser.objects.create_user(email ='gamekeeper@gmail.com', 
                                                         username = 'gamekeeper1', 
                                                         password = 'testpassword54321',
                                                         first_name = 'Game',
                                                         last_name = 'Keeper',
                                                         role = 'gameKeeper',
                                                         is_staff = True,
                                                         verified = True)
        
        # Creates initial balance for test gamekeeper to stop crash
        self.game_keeper_balance = UserBalance.objects.create(user_id = self.game_keeper)

class ShopTest(SetUpTest):

    def test_user_can_access_page(self):

        # Logins as test player, and tests if they can access the shop page
        self.client.login(username='player1', password='testpassword12345')
        response = self.client.get(self.shop_url)

        # Verifies the correct page is rendered
        self.assertEqual(response.status_code, 200) 
        self.assertTemplateUsed(response, 'shop/shop.html')

        # Verifies the page displays the correct items
        self.assertIn(self.digital_shop_item, response.context['items'])
        self.assertIn(self.non_digital_shop_item, response.context['items'])

    
    def test_buy_digital_item(self): 
        """Verifies the user can buy digital items, and the correct data is stored in the database"""
        # Logins as test player, and can buy digital item
        self.client.login(username='player1', password='testpassword12345')
        response = self.client.post(self.buy_digital_item_url)
        self.player_balance.refresh_from_db()


        self.assertEqual(response.status_code, 302) # Verifies the user is redirected
        self.assertEqual(self.player_balance.currency, 10) # Verifies the balance has 10 instead of 20 currency

        # Verifies a transaction is stored in db, and it has the correct attributes
        test_transaction = CurrencyTransaction.objects.get(transaction_id = 1)
        self.assertEqual(test_transaction.currency_difference, -10)
        self.assertEqual(test_transaction.description, f"Bought {self.digital_shop_item.name}")

        # Verifies the purchase is stored correctly in db
        test_purchase = ItemPurchase.objects.get(purchase_id = 1)
        self.assertEqual(test_purchase.user, self.player)
        self.assertEqual(test_purchase.item, self.digital_shop_item)
        self.assertTrue(test_purchase.is_digital)
        self.assertEqual(test_purchase.redeem_code, None)
        self.assertFalse(test_purchase.is_redeemed)

    def test_buy_non_digital_item(self): 
        """Verifies the user can buy non-digital items, and the correct data is stored in the db"""
        # Logins as test player, and buy non-digital item
        self.client.login(username='player1', password='testpassword12345')
        response = self.client.get(self.buy_non_digital_item_url)
        self.player_balance.refresh_from_db()

        
        self.assertEqual(response.status_code, 302) # Verifies the user is redirected
        self.assertEqual(self.player_balance.currency, 10) # Verifies the balance has 10 instead of 20 currency

        # Verifies a transaction is stored in db, and it has the correct attributes
        test_transaction = CurrencyTransaction.objects.get(transaction_id = 1)
        self.assertEqual(test_transaction.currency_difference, -10)
        self.assertEqual(test_transaction.description, f"Bought {self.non_digital_shop_item.name}")

        # Verifies the purchase is stored correctly in db
        test_purchase = ItemPurchase.objects.get(purchase_id = 1)
        self.assertEqual(test_purchase.user, self.player)
        self.assertEqual(test_purchase.item, self.non_digital_shop_item)
        self.assertFalse(test_purchase.is_digital)
        self.assertEqual(len(test_purchase.redeem_code), 6)
        self.assertFalse(test_purchase.is_redeemed)

class AddAndRemoveItemTest(SetUpTest):
    def test_player_cant_add_new_shop_item(self):
        """Verify players cant add new shop items"""
        self.client.login(username='player1', password='testpassword12345')
        response = self.client.post(reverse("shop:add_shop_item"), {
            "name": "test",
            "description": "test",
            "currency_cost": 20,
            "image": self.test_image,
            "is_digital": True,
        })
        self.assertRedirects(response, reverse("shop:shop"))
        self.assertEqual(ShopItem.objects.count(), 2)  

    def test_game_keeper_can_add_new_shop_item(self):
        """Verify game keepers can add new shop items"""
        self.client.login(username='gamekeeper1', password='testpassword54321')
        response = self.client.post(reverse("shop:add_shop_item"), {
            "name": "test",
            "description": "test",
            "currency_cost": 20,
            "image": self.test_image,
            "is_digital": True,
        })
        self.assertRedirects(response, reverse("shop:shop"))
        self.assertEqual(ShopItem.objects.count(), 3)  

    def test_player_cant_remove_shop_item(self):
        """Verify players can not remove shop items"""
        self.client.login(username='player1', password='testpassword12345')
        self.assertEqual(ShopItem.objects.count(), 2)  
        response = self.client.post(reverse("shop:remove_shop_item", args=[self.digital_shop_item.item_id]))
        self.assertRedirects(response, reverse("shop:shop"))
        self.assertTrue(ShopItem.objects.filter(item_id=self.digital_shop_item.item_id).exists()) 
        self.assertEqual(ShopItem.objects.count(), 2)  

    def test_game_keeper_can_remove_shop_item(self):
        """Verify game keepers can remove shop items, and refund users"""
        # Have player purchase item
        self.client.login(username='player1', password='testpassword12345')
        self.client.get(self.buy_digital_item_url)
        self.player_balance.refresh_from_db()
        self.assertEqual(self.player_balance.currency, 10) # Verifies amount after purchase

        self.client.login(username='gamekeeper1', password='testpassword54321')
        self.assertEqual(ShopItem.objects.count(), 2)  
        response = self.client.post(reverse("shop:remove_shop_item", args=[self.digital_shop_item.item_id]))
        self.assertRedirects(response, reverse("shop:shop"))
        self.assertEqual(ShopItem.objects.count(), 1)  
        self.player_balance.refresh_from_db()
        self.assertEqual(self.player_balance.currency, 20) # Verifies the player is refunded the currency
        self.assertEqual(CurrencyTransaction.objects.count(), 2)

class DisplayRedeemCodeTest(SetUpTest):
    def test_display_redeem_qr_code(self):
        """Verifies a player can access this page, and if it generates and displays the QR code for a purchase"""
        # Logins as test player, and buy non-digital item
        self.client.login(username='player1', password='testpassword12345')
        self.client.get(self.buy_non_digital_item_url)

        # Makes temp folder for qr_code, as @override_settings(MEDIA_ROOT=tempfile.mkdtemp()) is in use
        qr_code_dir = os.path.join(settings.MEDIA_ROOT, "qr_codes")
        os.makedirs(qr_code_dir, exist_ok=True)

        # Verifies the purchase's randomly generated redeem code can render the page
        test_purchase = ItemPurchase.objects.get(purchase_id = 1)
        response = self.client.get(reverse('shop:display_redeem_code', args=[test_purchase.redeem_code]))
        self.assertEqual(response.status_code, 200) # Would of been redirected (302) if wrong

        # Verifies the render includes a qr_code and the purchase
        self.assertIn('qr_code', response.context)
        self.assertIn('purchase', response.context)

    def test_unauthorised_user_redirected(self):
        """Verifies a non-player can't access this page, even if using correct correct url, and is redirected"""
        # Logins as test player, and buy non-digital item, then logout
        self.client.login(username='player1', password='testpassword12345')
        self.client.get(self.buy_non_digital_item_url)
        self.client.logout()

        # Logins as test game keeper, and trys to access page as unauthorised
        self.client.login(username='gamekeeper1', password='testpassword54321')
        test_purchase = ItemPurchase.objects.get(purchase_id = 1)
        response = self.client.get(reverse('shop:display_redeem_code', args=[test_purchase.redeem_code]))

        # Verifies the user is redirect to unauthorised.html page if they can't access page
        self.assertEqual(response.status_code, 302) 
        self.assertRedirects(response, self.shop_url)

class RedeemPageTest(SetUpTest): 
    def test_gamekeeper_can_access_redeem_page(self):
        """Verifies a game keeper can access this page"""
        # Logins as test game keeper, and attempt to access redeem_page
        self.client.login(username='gamekeeper1', password='testpassword54321')
        response = self.client.get(self.redeem_page_url)
        self.assertEqual(response.status_code, 200) 

    def test_player_cant_access_redeem_page(self):
        """Verifies a player can't access this page"""
        # Logins as test player, and attempt to access redeem_page
        self.client.login(username='player1', password='testpassword12345')
        response = self.client.get(self.redeem_page_url)

        # Verifies the user is redirected to unauthorised.html page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.shop_url)

    def test_gamekeeper_redirect_correctly_using_redeem_code(self):
        """Verifies the game keeper is sent to the correct page, if using the correct code"""
        # Logins as test player, and buy non-digital item, then logout
        self.client.login(username='player1', password='testpassword12345')
        self.client.get(self.buy_non_digital_item_url)
        self.client.logout()

        # Logins as test game keeper, and trys to access redeem_item page by inputing correct redeem 
        # code into redeem_page. 
        self.client.login(username='gamekeeper1', password='testpassword54321')
        test_purchase = ItemPurchase.objects.get(purchase_id = 1)
        response = self.client.post(self.redeem_page_url, {'redeem_code':test_purchase.redeem_code})

        # Verifies the game keeper is redirected to the correct page for redeeming items
        self.assertEqual(response.status_code, 302)
        redeem_item_url = reverse('shop:redeem_item', args=[test_purchase.redeem_code])
        self.assertRedirects(response, redeem_item_url)

    def test_inform_gamekeeper_invalid_redeem_code(self):
        """Verifies the gamekeeper is informed with the correct message if they input invalid code"""
        # Logins as test game keeper, and input wrong code into redeem page
        self.client.login(username='gamekeeper1', password='testpassword54321')
        response = self.client.post(self.redeem_page_url, {'redeem_code': 'invald'}) # Lowercase letters are never used for redeem code

        # Checks if view attempts render and displays correct message
        self.assertEqual(response.status_code, 200) 
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Invalid redeem code, please try again.')

class RedeemItemTest(SetUpTest):
    def test_gamekeeper_can_access_redeem_item(self):
        """Verifies a gamekeeper can access the redeem item page if using the correct code"""
        # Logins as test player, and buy non-digital item, then logout
        self.client.login(username='player1', password='testpassword12345')
        self.client.get(self.buy_non_digital_item_url)
        self.client.logout()

        # Logins as test game keeper, and verifies they can access redeem_item page using correct redeem code
        self.client.login(username='gamekeeper1', password='testpassword54321')
        test_purchase = ItemPurchase.objects.get(purchase_id = 1)
        redeem_item_url = reverse('shop:redeem_item', args=[test_purchase.redeem_code])
        response = self.client.get(redeem_item_url)
        self.assertEqual(response.status_code, 200)

    def test_player_cant_access_redeem_item(self):
        """Verifies a player can't access the redeem_item page, and is redirect to the correct page"""
        # Logins as test player, and buy non-digital item, then attempt to access redeem item page
        self.client.login(username='player1', password='testpassword12345')
        self.client.get(self.buy_non_digital_item_url)
        test_purchase = ItemPurchase.objects.get(purchase_id = 1)
        redeem_item_url = reverse('shop:redeem_item', args=[test_purchase.redeem_code])
        response = self.client.get(redeem_item_url)

        # Verifies the user is redirected to the shop page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.shop_url)

    
    def test_gamekeeper_can_redeem_item(self):
        """Verifies a game keeper can redeem an item through POST, and the item is redeemed, and if they are redirected"""
        # Logins as test player, and buy non-digital item, then logout
        self.client.login(username='player1', password='testpassword12345')
        self.client.get(self.buy_non_digital_item_url)
        self.client.logout()

        # Logins as test game keeper, and accesses redeem_item 
        self.client.login(username='gamekeeper1', password='testpassword54321')
        test_purchase = ItemPurchase.objects.get(purchase_id = 1)
        redeem_item_url = reverse('shop:redeem_item', args=[test_purchase.redeem_code])

        response = self.client.post(redeem_item_url) # Cause a post response on view

        # Verifies the purchase has been redeemed
        test_purchase.refresh_from_db()
        self.assertEqual(test_purchase.is_redeemed, True)

        # Verifies they redirected to the correct page
        self.assertRedirects(response, self.redeem_page_url)


class RefundPurchasedItemTest(SetUpTest):
    def test_player_can_refund_non_digital_unredeemed_item(self):
        """Verify players should be able to refund non digital unredeemed shop items"""
        self.client.login(username='player1', password='testpassword12345')
        self.assertEqual(self.player_balance.currency, 20) # Verifiy starting balance
        self.non_digital_purchase = ItemPurchase.objects.create(user=self.player, item=self.non_digital_shop_item, is_digital=False, is_redeemed=False)

        response = self.client.post(reverse("shop:refund_item", args=[self.non_digital_purchase.purchase_id]))
        self.player_balance.refresh_from_db()

        self.assertRedirects(response, reverse("shop:purchased_items"))
        self.assertEqual(self.player_balance.currency, 30) # Verify balance increase
        self.assertFalse(ItemPurchase.objects.filter(purchase_id=self.non_digital_purchase.purchase_id).exists())  # Purchase should be deleted
        self.assertEqual(CurrencyTransaction.objects.count(), 1) # Verify refund transaction is recorded

    def test_players_cannot_refund_redeemed_item(self):
        """Verify players shouldnt be able to refund redeemed shop items"""
        self.client.login(username='player1', password='testpassword12345')
        self.assertEqual(self.player_balance.currency, 20) # Verifiy starting balance
        self.redeemed_purchase = ItemPurchase.objects.create(user=self.player, item=self.non_digital_shop_item, is_digital=False, is_redeemed=True)

        response = self.client.post(reverse("shop:refund_item", args=[self.redeemed_purchase.purchase_id]))
        self.player_balance.refresh_from_db()

        self.assertRedirects(response, reverse("shop:purchased_items"))
        self.assertTrue(ItemPurchase.objects.filter(purchase_id=self.redeemed_purchase.purchase_id).exists())  # Purchase should still exist
        self.assertEqual(self.player_balance.currency, 20) # Verifiy balance remains unchanged
        self.assertEqual(CurrencyTransaction.objects.count(), 0) # Verify no refund transaction is recorded

    def test_players_cannot_refund_digital_item(self):
        """Verify players shouldnt be able to refund digital shop items"""
        self.client.login(username='player1', password='testpassword12345')
        self.assertEqual(self.player_balance.currency, 20) # Verifiy starting balance
        self.digital_purchase = ItemPurchase.objects.create(user=self.player, item=self.non_digital_shop_item, is_digital=True, is_redeemed=False)

        response = self.client.post(reverse("shop:refund_item", args=[self.digital_purchase.purchase_id]))
        self.player_balance.refresh_from_db()

        self.assertRedirects(response, reverse("shop:purchased_items"))
        self.assertTrue(ItemPurchase.objects.filter(purchase_id=self.digital_purchase.purchase_id).exists())  # Purchase should still exist
        self.assertEqual(self.player_balance.currency, 20) # Verifiy balance remains unchanged
        self.assertEqual(CurrencyTransaction.objects.count(), 0) # Verify no refund transaction is recorded

    def test_user_cannot_refund_item_not_owned_by_user(self):
        """Verify users shouldnt be able to refund item purchase not owned by them"""
        self.non_digital_purchase = ItemPurchase.objects.create(user=self.game_keeper, item=self.non_digital_shop_item, is_digital=False, is_redeemed=False)

        self.client.login(username='player1', password='testpassword12345')

        response = self.client.post(reverse("shop:refund_item", args=[self.non_digital_purchase.purchase_id]))

        self.assertRedirects(response, reverse("shop:purchased_items"))
        self.assertTrue(ItemPurchase.objects.filter(purchase_id=self.non_digital_purchase.purchase_id).exists())  # Purchase should still exist
        self.assertEqual(self.player_balance.currency, 20) # Verifiy balance remains unchanged


