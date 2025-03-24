from celery.schedules import crontab
from celery import Celery, shared_task
from django.utils.timezone import now, timedelta
from .models import QuizDailyStreak

app = Celery('sustainableCampus')

@shared_task
def reset_daily_streak():
    """This task resets all daily quiz streaks of players who did not complete the quiz yesterday """
    yesterday = now().date() - timedelta(days=1)  # Yesterday's date

    # Retrieves all streaks of players who did not do yesterday quiz
    streaks = QuizDailyStreak.objects.filter(last_completed_quiz_date__lt=yesterday)

    # Reset the streak for each user who missed yesterday's quiz
    for streak in streaks:
        streak.current_streak = 0
        streak.save()

