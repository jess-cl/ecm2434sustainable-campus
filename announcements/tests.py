from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from announcements.forms import AnnouncementForm
from announcements.models import Announcement
from accounts.models import CustomUser
from django.utils.timezone import now
from .models import Announcement, Event, EventAttended
from shop.models import UserBalance, CurrencyTransaction
from datetime import date

# Create your tests here.

User = get_user_model()

class AnnouncementFormTests(TestCase):
    def test_valid_form(self):
        """Test that the form is valid when given correct data"""
        form_data = {"title": "Test Announcement", "summary":"test summary", "content": "This is a test announcement."}
        form = AnnouncementForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_missing_title(self):
        """Test that the form is invalid when title is missing"""
        form_data = {"title": "", "content": "This is a test announcement."}
        form = AnnouncementForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

    def test_missing_content(self):
        """Test that the form is invalid when content is missing"""
        form_data = {"title": "Test Announcement", "content": ""}
        form = AnnouncementForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("content", form.errors)

    def test_title_max_length(self):
        """Test that the title cannot exceed 200 characters"""
        long_title = "A" * 201  # 201 characters
        form_data = {"title": long_title, "content": "Valid content"}
        form = AnnouncementForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

class AnnouncementModelTests(TestCase):
    def setUp(self):
        """Set up test data for users and announcements"""
        self.user = CustomUser.objects.create_user(username="testuser", password="password", role="game_keeper") # creating an example user
        self.announcement = Announcement.objects.create(
            title="Test Announcement",
            content="This is a test announcement.",
            author=self.user
        )

    def test_announcement_creation(self):
        """Test that an announcement is created correctly"""
        self.assertEqual(self.announcement.title, "Test Announcement") # makes sure the post matches the users post
        self.assertEqual(self.announcement.content, "This is a test announcement.")
        self.assertEqual(self.announcement.author, self.user)
        self.assertTrue(self.announcement.created_at)  # Ensure timestamp is auto-generated

    def test_announcement_str(self):
        """Test the __str__ method of Announcement"""
        self.assertEqual(str(self.announcement), "Test Announcement")

    def test_get_author_role(self):
        """Test get_author_role method"""
        self.assertEqual(self.announcement.get_author_role(), "game_keeper")  # Role should match the user



class AnnouncementViewTests(TestCase):
    def setUp(self):
        """Set up test data for users and announcements"""
        self.client = Client()

        # Create users: a Game Keeper and a Player
        self.game_keeper = CustomUser.objects.create_user(username="gamekeeper", password="TestPassword12345", role="gameKeeper", verified=True)
        self.player = CustomUser.objects.create_user(username="player", password="TestPassword12345", role="player", verified=True)

        self.player_balance = UserBalance.objects.create(user_id=self.player, currency=0)

        # Create a valid announcement with no event
        self.announcement = Announcement.objects.create(
            title="Test Announcement",
            summary="test summary",
            content="test content.",
            image=None,
            author=self.game_keeper
        )

        # Create a valid event
        self.event = Event.objects.create(
            announcement=self.announcement,
            currency_reward=100,
            transaction_description="Test reward",
            event_date=now().date(),
            event_code="EVENTCODE"
        )

        # Create a valid announcement with an event
        self.valid_announcement_with_event={
            'title': 'Test Announcement with Event',
            'summary': "test summary",
            'content': "test content with event.",
            'is_event': True,
            'currency_reward': 50,
            'transaction_description': 'test event',
            'event_date': now().date(),
        }

    def test_announcement_list_view(self):
        """Ensure announcement list view is accessible"""
        self.client.login(username="player", password="TestPassword12345")
        response = self.client.get(reverse("announcements:announcement_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Announcement")

    def test_create_announcement_requires_login(self):
        """Ensure unauthenticated users are redirected to login page"""
        response = self.client.get(reverse("announcements:create_announcement"))
        self.assertRedirects(response, "/accounts/login/?next=/announcements/create/")

    def test_create_announcement_by_game_keeper(self):
        """Verifies a game keeper can create an announcement using valid form inputs"""
        self.client.login(username='gamekeeper', password='TestPassword12345')
        response = self.client.post(reverse('announcements:create_announcement'), self.valid_announcement_with_event)

        self.assertEqual(response.status_code, 302)  
        self.assertEqual(Announcement.objects.count(), 2)  
        self.assertEqual(Event.objects.count(), 2)  

    def test_create_announcement_cant_be_used_by_player(self):
        """Verifies a player can't create an announcement, even with valid form inputs"""
        self.client.login(username='player', password='TestPassword12345')
        response = self.client.post(reverse('announcements:create_announcement'), self.valid_announcement_with_event)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Announcement.objects.count(), 1)
        self.assertEqual(Event.objects.count(), 1)  

    def test_redeem_event_reward_on_events_day_rewards_player(self):
        """Verifies a player can redeem an event's attendence reward if they scan the code on the correct day"""
        self.client.login(username="player", password="TestPassword12345")
        response = self.client.get(reverse('announcements:redeem_event_reward', args=[self.event.event_code]))
        self.player.refresh_from_db()
        self.player_balance.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(EventAttended.objects.count(), 1)
        self.assertTrue(EventAttended.objects.filter(player=self.player, event=self.event).exists())
        self.assertEqual(self.player_balance.currency, 100)
        self.assertEqual(CurrencyTransaction.objects.count(), 1)

    def test_redeem_event_reward_before_events_day_does_not_reward_player(self):
        """Verifies a player cant redeem an event's attendence reward if they scan the code before the correct day"""
        self.event.event_date = date(2000, 1, 1)
        self.event.save()

        self.client.login(username="player", password="TestPassword12345")
        response = self.client.get(reverse('announcements:redeem_event_reward', args=[self.event.event_code]))
        self.player.refresh_from_db()
        self.player_balance.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(EventAttended.objects.count(), 0)
        self.assertFalse(EventAttended.objects.filter(player=self.player, event=self.event).exists())
        self.assertEqual(self.player_balance.currency, 0)
        self.assertEqual(CurrencyTransaction.objects.count(), 0)

    def test_redeem_event_reward_after_events_day_does_not_reward_player(self):
        """Verifies a player cant redeem an event's attendence reward if they scan the code after the correct day"""
        self.event.event_date = date(2100, 1, 1)
        self.event.save()

        self.client.login(username="player", password="TestPassword12345")
        response = self.client.get(reverse('announcements:redeem_event_reward', args=[self.event.event_code]))
        self.player.refresh_from_db()
        self.player_balance.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(EventAttended.objects.count(), 0)
        self.assertFalse(EventAttended.objects.filter(player=self.player, event=self.event).exists())
        self.assertEqual(self.player_balance.currency, 0)
        self.assertEqual(CurrencyTransaction.objects.count(), 0)

    def test_redeem_event_reward_doesnt_reward_player_twice_when_used_twice(self):
        """Verifies a player cant redeem an event's attendence reward twice to get the same reward twice"""
        self.client.login(username="player", password="TestPassword12345")
        self.client.get(reverse('announcements:redeem_event_reward', args=[self.event.event_code]))
        response = self.client.get(reverse('announcements:redeem_event_reward', args=[self.event.event_code]))
        self.player.refresh_from_db()
        self.player_balance.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/announcements/')
        self.assertEqual(EventAttended.objects.count(), 1)
        self.assertTrue(EventAttended.objects.filter(player=self.player, event=self.event).exists())
        self.assertEqual(self.player_balance.currency, 100)
        self.assertEqual(CurrencyTransaction.objects.count(), 1)

    def test_display_event_qr_code_can_be_accessed_by_gamekeeper(self):
        """Verifies a game keeper can access the display event qr code page"""
        self.client.login(username='gamekeeper', password='TestPassword12345')
        response = self.client.get(reverse('announcements:display_event_qr_code', args=[self.event.event_code]))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'announcements/display_event_qr_code.html')

    def test_display_event_qr_code_can_not_be_accessed_by_player(self):
        """Verifies a player cant access the display event qr code page"""
        self.client.login(username='player', password='TestPassword12345')
        response = self.client.get(reverse('announcements:display_event_qr_code', args=[self.event.event_code]))
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/announcements/')

    def test_user_can_like_announcement(self):
        """Verififies a player and game keeper can like an announcement"""
        self.assertEqual(self.announcement.likes.count(), 0) # Verifies annoucment has no likes before test

        self.client.login(username="player", password="TestPassword12345")
        self.client.get(reverse('announcements:like_announcement', args=[self.announcement.id]))
        self.client.logout()

        self.client.login(username="gamekeeper", password="TestPassword12345")
        response = self.client.get(reverse('announcements:like_announcement', args=[self.announcement.id]))

        self.announcement.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.announcement.likes.count(), 2)

    def test_user_can_unlike_announcement(self):
        """Verififies a user can unlike an announcement"""
        self.client.login(username="player", password="TestPassword12345")
        self.client.get(reverse('announcements:like_announcement', args=[self.announcement.id]))
        response = self.client.get(reverse('announcements:like_announcement', args=[self.announcement.id]))

        self.announcement.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.announcement.likes.count(), 0)

    def test_user_can_only_like_or_dislike_an_announcement_not_both(self):
        """Verififies a user can not test"""
        self.client.login(username="player", password="TestPassword12345")
        self.client.get(reverse('announcements:like_announcement', args=[self.announcement.id]))
        response = self.client.get(reverse('announcements:dislike_announcement', args=[self.announcement.id]))

        self.announcement.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.announcement.likes.count(), 0)
        self.assertEqual(self.announcement.dislikes.count(), 1)

        response = self.client.get(reverse('announcements:like_announcement', args=[self.announcement.id]))

        self.announcement.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.announcement.likes.count(), 1)
        self.assertEqual(self.announcement.dislikes.count(), 0)

    def test_user_can_dislike_announcement(self):
        """Verififies a player and game keeper can like an announcement"""
        self.assertEqual(self.announcement.dislikes.count(), 0) # Verifies annoucment has no dislikes before test

        self.client.login(username="player", password="TestPassword12345")
        self.client.get(reverse('announcements:dislike_announcement', args=[self.announcement.id]))
        self.client.logout()

        self.client.login(username="gamekeeper", password="TestPassword12345")
        response = self.client.get(reverse('announcements:dislike_announcement', args=[self.announcement.id]))

        self.announcement.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.announcement.dislikes.count(), 2)

    def test_user_can_undislike_announcement(self):
        """Verififies a user can undislike an announcement"""
        self.client.login(username="player", password="TestPassword12345")
        self.client.get(reverse('announcements:dislike_announcement', args=[self.announcement.id]))
        response = self.client.get(reverse('announcements:dislike_announcement', args=[self.announcement.id]))

        self.announcement.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.announcement.dislikes.count(), 0)

    