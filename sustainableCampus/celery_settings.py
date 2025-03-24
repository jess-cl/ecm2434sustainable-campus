from celery.schedules import crontab
CELERY_BEAT_SCHEDULE = {
    # Reset the daily streaks of every player at midnight every day if they miss a quiz
    'reset_daily_streak_midnight': {
        'task': 'dailyQuiz.tasks.reset_daily_streak',
        'schedule': crontab(minute=0, hour=0),
    },
    # Rewards the top 10 forest players on the leaderboard every Saturday at midnight
    'reward_top_forest_players_every_saturday': {
        'task': 'leaderboards.tasks.reward_top_forest_players',
        'schedule': crontab(minute=0, hour=0, day_of_week='saturday'),
    },
    # Rewards top top 10 daily quiz players on the leaderboard every Saturday at midnight
    'reward_top_daily_quiz_players_every_saturday': {
        'task': 'leaderboards.tasks.reward_top_daily_quiz_players',
        'schedule': crontab(minute=0, hour=0, day_of_week='saturday'),
    },
}