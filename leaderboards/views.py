from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import TreeScore

@login_required
def leaderboard(request):
    # Retrieves the top 10 players with the highest number of trees grown
    all_player_scores = TreeScore.objects.order_by('-score')

    user_score = None
    user_rank = None

    # Retrieves the logged-in user score if they are a player
    if request.user.role == 'player':
        try: 
            user_score = TreeScore.objects.get(user=request.user)

            user_rank = 0
            while True:
                user_rank += 1
                if all_player_scores[user_rank - 1] == user_score:
                    break

        except TreeScore.DoesNotExist:
            messages.error(request, "Your score could not be found.")
            user_score = None


    context = {'top_players':all_player_scores[:10], 'user_score':user_score, 'user_rank': user_rank}
    return render(request, 'leaderboards/leaderboards.html', context)

