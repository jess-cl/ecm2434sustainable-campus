from django.test import TestCase
from main.models import UserHighScore
from dailyQuiz.models import QuizDailyStreak
from .tasks import reward_top_forest_players, reward_top_daily_quiz_players
from shop.models import UserBalance, CurrencyTransaction
from accounts.models import CustomUser
from django.urls import reverse
# Create your tests here.

class SetUpTest(TestCase):
    def setUp(self):
        self.leaderboard_url=reverse('leaderboards:forest_leaderboard')
        
        # Creates 20 different users, with different usernames and emails. All have a different score
        self.users = []
        for i in range(20): 
            user = CustomUser.objects.create_user(username = f'{i}', email = f'{i}@gmail.com', password = 'TestPassword12345')
            self.users.append(user)
            UserHighScore.objects.create(user=user, high_score=i)

            UserBalance.objects.create(user_id=user, currency=0)


class LeaderboardTest(SetUpTest):
    def test_user_can_access_leaderboard_page(self):
        """Verifies the user can access the leaderboard page"""
        self.client.login(username='7', password='TestPassword12345')
        response = self.client.get(self.leaderboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'leaderboards/leaderboards.html')

    def test_user_can_view_top_10_scores(self):
        """Verifies the user can view the top 10 scores on the leader board, and they are correct, and in order"""
        self.client.login(username='7', password='TestPassword12345')
        response = self.client.get(self.leaderboard_url)

        top_10_scores = response.context['top_players']
        scores = UserHighScore.objects.order_by('-high_score')

        self.assertQuerySetEqual(top_10_scores, scores[:10])

    def test_user_view_personal_score_and_rank(self):
        """Verifies the user can see their score and rank on the leaderboard, even when not in the top 10"""
        self.client.login(username='7', password='TestPassword12345')
        response = self.client.get(self.leaderboard_url)

        user_rank = response.context['user_rank']
        user_score = response.context['user_score']

        self.assertEqual(user_rank, 13)
        self.assertEqual(user_score.high_score, 7)

class ForestRewardTopPlayersTest(SetUpTest):
    def test_top_10_forest_players_are_rewarded(self):
        """Verify the top 10 players recieve the correct reward"""
        reward_top_forest_players.apply()

        top_10_players = UserHighScore.objects.order_by('-high_score')[:10]
        reward_amounts = [100, 75, 50, 25, 25, 25, 25, 25, 25, 25]
        count = 0

        for player in top_10_players:
            user_balance = UserBalance.objects.get(user_id=player.user)
            self.assertEqual(user_balance.currency, reward_amounts[count])

            transaction = CurrencyTransaction.objects.filter(user=player.user).first()
            self.assertEqual(transaction.currency_difference, reward_amounts[count])
            self.assertEqual(transaction.description, "Weekly reward for being a top player in the forest leaderboard")

            count = count + 1

    def test_below_top_10_forest_players_are_not_rewarded(self):
        """Verify that players not in the top 10 don't recieve the rewards.."""
        reward_top_forest_players.apply()

        bottom_10_players = UserHighScore.objects.order_by('-high_score')[10:]
        for player in bottom_10_players:
            user_balance = UserBalance.objects.get(user_id=player.user)
            self.assertEqual(user_balance.currency, 0)  # No reward given

            # Ensure no transaction exists for them
            transaction = CurrencyTransaction.objects.filter(user=player.user).first()
            self.assertIsNone(transaction)

class DailyQuizRewardTopPlayersTest(SetUpTest):
    def test_top_10_daily_quiz_players_are_rewarded(self):
        """Verify the top 10 players recieve the correct reward"""
        reward_top_daily_quiz_players.apply()

        top_10_players = QuizDailyStreak.objects.order_by('-current_streak')[:10]
        reward_amounts = [100, 75, 50, 25, 25, 25, 25, 25, 25, 25]
        count = 0

        for player in top_10_players:
            user_balance = UserBalance.objects.get(user_id=player.user)
            self.assertEqual(user_balance.currency, reward_amounts[count])

            transaction = CurrencyTransaction.objects.filter(user=player.user).first()
            self.assertEqual(transaction.currency_difference, reward_amounts[count])
            self.assertEqual(transaction.description, "Weekly reward for being a top player in the daily quiz leaderboard")

            count = count + 1

    def test_below_top_10_daily_quiz_players_are_not_rewarded(self):
        """Verify that players not in the top 10 don't recieve the rewards.."""
        reward_top_daily_quiz_players.apply()

        bottom_10_players = QuizDailyStreak.objects.order_by('-current_streak')[10:]
        for player in bottom_10_players:
            user_balance = UserBalance.objects.get(user_id=player.user)
            self.assertEqual(user_balance.currency, 0)  # No reward given

            # Ensure no transaction exists for them
            transaction = CurrencyTransaction.objects.filter(user=player.user).first()
            self.assertIsNone(transaction)
