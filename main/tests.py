from django.test import TestCase
from django.urls import reverse
from accounts.models import CustomUser
from .models import UserInventory, UserForest, Plant, UserHighScore
from .views import calculate_forest_value
import datetime

# set up

class SetUpModels(TestCase):
    def setUp(self):
        # urls used in tests
        self.collect_red = reverse('main:claim_red_marker')
        self.collect_blue = reverse('main:claim_blue_marker')
        self.collect_green = reverse('main:claim_green_marker')

        # creates a test user, as all models except plant have a user_id as a foreign key
        self.test_user = CustomUser.objects.create_user(
            email = 'test_user@gmail.com',
            username = 'test_user',
            password = 'Testing123',
            first_name = 'Test',
            last_name = 'User',
            role = 'player',
            verified = True
        )

        # generates default inventory, forest, and high score for the new user
        self.test_inventory = UserInventory(user_id = self.test_user.id)
        self.test_forest = UserForest(user_id = self.test_user.id)
        self.test_score = UserHighScore(user_id = self.test_user.id)
        # plants is not specific to a user; all user's will use the same table
        plant_1 = Plant(requirement_type=0, rarity=0, plant_name="Oak Tree")
        plant_1.save()
        plant_2 = Plant(requirement_type=2, rarity=0, plant_name="Birch Tree")
        plant_2.save()
        plant_3 = Plant(requirement_type=2, rarity=1, plant_name="Fir Tree")
        plant_3.save()
        plant_4 = Plant(requirement_type=1, rarity=1, plant_name="Red Campion")
        plant_4.save()
        plant_5 = Plant(requirement_type=0, rarity=0, plant_name="Poppy")
        plant_5.save()
        plant_6 = Plant(requirement_type=1, rarity=2, plant_name="Cotoneaster")
        plant_6.save()



# testing models

class CheckDefaults(SetUpModels):
    def test_check_if_default_inv_valid(self):
        """Default inventory for a new user is valid"""
        default_inv = self.test_inventory
        self.assertEqual(default_inv.paper, 0)
        self.assertEqual(default_inv.plastic, 0)
        self.assertEqual(default_inv.compost, 0)
        self.assertEqual(default_inv.recycled_paper, 0)
        self.assertEqual(default_inv.recycled_plastic, 0)
        self.assertEqual(default_inv.recycled_compost, 0)
        self.assertEqual(default_inv.tree_guard, 0)
        self.assertEqual(default_inv.rain_catcher, 0)
        self.assertEqual(default_inv.fertilizer, 0)
        self.assertEqual(default_inv.oak, 0)
        self.assertEqual(default_inv.birch, 0)
        self.assertEqual(default_inv.fir, 0)
        self.assertEqual(default_inv.red_campion, 0)
        self.assertEqual(default_inv.poppy, 0)
        self.assertEqual(default_inv.cotoneaster, 0)
        self.assertEqual(default_inv.collected_markers, "")
        self.assertEqual(default_inv.last_collected, str(datetime.date))
    
    def test_check_if_default_forest_valid(self):
        """Default forest for a new user is valid"""
        default_forest = self.test_forest
        self.assertEqual(default_forest.cells, "0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0")
        self.assertEqual(default_forest.last_growth_check_date, str(datetime.date))

    def test_check_if_default_high_score_valid(self):
        """Default high score for a new user is valid"""
        default_score = self.test_score
        self.assertEqual(default_score.high_score, 0)

# testing views

class ForestTest(SetUpModels):
    def test_calculate_forest_value(self):
        """Checks if the value calculated by the function is correct for a forest with a known value."""
        # this forest has a pre-calculated value of 260
        self.test_forest.cells = "6,2,0;4,2,0;1,1,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0"
        self.assertEqual(calculate_forest_value(self.test_forest), '260')