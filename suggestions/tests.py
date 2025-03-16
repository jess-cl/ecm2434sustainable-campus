from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from accounts.models import CustomUser
from .models import Suggestion
import os
import glob
from django.conf import settings
from django.test import override_settings
import tempfile

# Create your tests here.
class SetUpTest(TestCase):
    def setUp(self):
        self.create_suggestion_url = reverse('suggestions')
        self.view_suggestions_url = reverse('view_suggestions')

        # Creates a test player account
        self.player = CustomUser.objects.create_user(email ='player@gmail.com', 
                                                    username = 'player1', 
                                                    password = 'testpassword12345',
                                                    first_name = 'Player',
                                                    last_name = 'User',
                                                    role = 'player',
                                                    verified = True)

        # Creates a test game keeper account
        self.game_keeper = CustomUser.objects.create_user(email ='gamekeeper@gmail.com', 
                                                         username = 'gamekeeper1', 
                                                         password = 'testpassword54321',
                                                         first_name = 'Game',
                                                         last_name = 'Keeper',
                                                         role = 'gameKeeper',
                                                         is_staff = True,
                                                         verified = True)
        
        # Creates a test suggestion, made by a player
        self.player_test_suggestion = Suggestion.objects.create(
            user=self.player, content="test player suggestion content", category="other"
        )

        # Creates a test suggestion, made by a game keeper
        self.game_keeper_test_suggestion = Suggestion.objects.create(
            user=self.game_keeper, content="test game keeper suggestion content", category="bug"
        )

        # Url for deleting player test suggestion
        self.delete_player_test_suggestion_url = reverse('delete_suggestion', args=[self.player_test_suggestion.id])
        
        # Url for deleting game keeper test suggestion
        self.delete_game_keeper_test_suggestion_url = reverse('delete_suggestion', args=[self.game_keeper_test_suggestion.id])

class TestCreateSuggestionTests(SetUpTest):
    def test_user_can_submit_valid_suggestion(self):
        """Verify a valid suggestion is successfully submitted"""
        self.client.login(username="player1", password="testpassword12345")
        response = self.client.post(self.create_suggestion_url, {"suggestion": "new suggestion", "category": "other"})
        self.assertEqual(Suggestion.objects.count(), 3)
        self.assertRedirects(response, self.create_suggestion_url)

    def test_user_cant_submit_suggestion_with_short_content(self):
        """Verify a suggestion that are too short in content are rejected"""
        self.client.login(username="player1", password="testpassword12345")
        response = self.client.post(self.create_suggestion_url, {"suggestion": "test", "category": "other"})
        self.assertEqual(Suggestion.objects.count(), 2)
        self.assertRedirects(response, self.create_suggestion_url)

    def test_user_cant_submit_suggestion_with_invalid_category(self):
        """Verify a suggestion that are too short in content are rejected"""
        self.client.login(username="player1", password="testpassword12345")
        response = self.client.post(self.create_suggestion_url, {"suggestion": "new suggestion", "category": "invalid category"})
        self.assertEqual(Suggestion.objects.count(), 2)
        self.assertRedirects(response, self.create_suggestion_url)

class TestViewSuggestionsTests(SetUpTest):
    def test_user_can_view_suggestions(self):
        """Verifies user can view the suggestions"""
        self.client.login(username="gamekeeper1", password="testpassword54321")
        response = self.client.get(self.view_suggestions_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "test player suggestion content")
        self.assertContains(response, "test game keeper954 suggestion content")

class TestDeleteSuggestionsTests(SetUpTest):
    def test_player_can_delete_own_suggestion(self):
        """Verifies a player can delete a suggestion they created"""
        self.client.login(username="player1", password="testpassword12345")
        response = self.client.post(self.delete_player_test_suggestion_url)
        self.assertEqual(Suggestion.objects.count(), 1)
        self.assertRedirects(response, self.view_suggestions_url)

    def test_player_cant_delete_other_user_suggestions(self):
        """Verifies a player cant delete a suggestion they did not create"""
        self.client.login(username="player1", password="testpassword12345")
        response = self.client.post(self.delete_game_keeper_test_suggestion_url)
        self.assertEqual(Suggestion.objects.count(), 2)  
        self.assertRedirects(response, reverse("view_suggestions"))

    def test_game_keeper_can_delete_other_user_suggestions(self):
        """Verifies a game keeper can delete a suggestion created by another user"""
        self.client.login(username="player1", password="testpassword12345")
        response = self.client.post(self.delete_player_test_suggestion_url)
        self.assertEqual(Suggestion.objects.count(), 1)
        self.assertRedirects(response, self.view_suggestions_url)