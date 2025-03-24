from celery import shared_task
from shop.models import UserBalance, CurrencyTransaction
from main.models import UserHighScore
from dailyQuiz.models import QuizDailyStreak
from celery.schedules import crontab
from celery import Celery

app = Celery('sustainableCampus')

@shared_task
def reward_top_forest_players():
    """Ensures the top 10 forest players are rewarded every Saturday."""

    top_10_players = UserHighScore.objects.order_by('-high_score')[:10]
    reward_amount = [100, 75, 50, 25, 25, 25, 25, 25, 25, 25]
    count = 0

    for player in top_10_players:
        user = player.user
        user_balance = UserBalance.objects.get(user_id=user)

        # Update balance
        user_balance.currency += reward_amount[count]
        user_balance.save()

        # Create a transaction record for each user in the top 10 who are rewarded
        CurrencyTransaction.objects.create(
            user=user,
            currency_difference=reward_amount[count],
            description=f"Weekly reward for being a top player in the forest leaderboard",
            game_keeper=None
        )

        count += 1



@shared_task
def reward_top_daily_quiz_players():
    """Ensures the top 10 daily quiz players are rewarded every Saturday."""

    top_10_players = QuizDailyStreak.objects.order_by('-current_streak')[:10]
    reward_amount = [100, 75, 50, 25, 25, 25, 25, 25, 25, 25]
    count = 0

    for player in top_10_players:
        user = player.user
        user_balance = UserBalance.objects.get(user_id=user)

        # Update balance
        user_balance.currency += reward_amount[count]
        user_balance.save()

        # Create a transaction record for each user in the top 10 who are rewarded
        CurrencyTransaction.objects.create(
            user=user,
            currency_difference=reward_amount[count],
            description=f"Weekly reward for being a top player in the daily quiz leaderboard",
            game_keeper=None
        )

        count += 1