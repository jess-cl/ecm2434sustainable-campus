from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from main.models import UserHighScore
from dailyQuiz.models import QuizDailyStreak

@login_required
def forest_leaderboard(request):
    # Retrieves the top 10 players with the highest land sell
    all_player_scores = UserHighScore.objects.filter(user__role='player').order_by('-high_score')

    user_score = None
    user_rank = None

    # Retrieves the logged-in user score if they are a player, and determines their rank in the leaderboard
    if request.user.role == 'player':
        try: 
            user_score = UserHighScore.objects.get(user=request.user)

            user_rank = 0
            while True:
                user_rank += 1
                if all_player_scores[user_rank - 1] == user_score:
                    break
                
        except UserHighScore.DoesNotExist:
            messages.error(request, "Your forest high score could not be found.")
            user_score = None


    context = {'top_players':all_player_scores[:10], 'user_score':user_score, 'user_rank': user_rank}
    return render(request, 'leaderboards/leaderboards.html', context)

@login_required
def daily_streak_leaderboard(request):
    # Retrieves all player quiz daily streaks, and orders them by largest to smallest
    all_player_daily_streaks = QuizDailyStreak.objects.filter(user__role='player').order_by('-current_streak')

    user_daily_streak = None
    user_rank = None

    # Retrieves the logged-in user score if they are a player
    if request.user.role == 'player':
        try: 
            user_daily_streak = QuizDailyStreak.objects.get(user=request.user)

            user_rank = 0
            while True:
                user_rank += 1
                if all_player_daily_streaks[user_rank - 1] == user_daily_streak:
                    break

        except QuizDailyStreak.DoesNotExist:
            messages.error(request, "Your quiz daily streak could not be found.")
            user_daily_streak = None

    context = {'top_players':all_player_daily_streaks[:10], 'user_daily_streak':user_daily_streak, 'user_rank': user_rank}
    return render(request, 'leaderboards/daily_streak_leaderboard.html', context)