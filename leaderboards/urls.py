from django.urls import path
from . import views

app_name = 'leaderboards'

urlpatterns = [
    path("forest", views.forest_leaderboard, name="forest_leaderboard"),
    path("daily-streaks", views.daily_streak_leaderboard, name="daily_streak_leaderboard")
]
