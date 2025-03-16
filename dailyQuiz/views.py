from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import QuizQuestion, QuizAttempt, QuizDailyStreak
from .forms import QuizQuestionForm
import random
# Create your views here.


def quiz_home(request):
    # load the html
    return render(request, 'dailyQuiz/quiz_home.html')



# Retreives and displays all daily quiz questions on the list_questions html page
@login_required
def list_quiz_questions(request):
    if request.user.role == 'player':
        messages.error(request, "You must be a Game Keeper or Developer to access this page.")    
        return redirect('dailyQuiz:quiz_home')

    questions=QuizQuestion.objects.all()
    context = {'questions': questions}
    return render(request, 'dailyQuiz/list_questions.html', context)

# Creates a new quiz question using the inputs from the QuizQuestionForm
@login_required
def create_quiz_question(request):
    # Ensures only a game keeper or developer can access this page
    if request.user.role == 'player':
        messages.error(request, "You must be a Game Keeper or Developer to access this page.")    
        return redirect('dailyQuiz:quiz_home')

    if request.method == 'POST':
        form = QuizQuestionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Creation of new quiz question successful!")
            return redirect('dailyQuiz:list_questions')
        
    form = QuizQuestionForm()    
        
    context = {'form': form}
    return render(request, 'dailyQuiz/create_question.html', context)

# Used to delete a quiz question
@login_required
def delete_quiz_question(request, question_id):
    # Ensures only a game keeper or developer can access this page
    if request.user.role == 'player':
        messages.error(request, "You must be a Game Keeper or Developer to access this page.")    
        return redirect('dailyQuiz:quiz_home')
    
    # Retrives the question using given id, checks if it exists, else returns an error message
    try:
        question = QuizQuestion.objects.get(id=question_id)
    except QuizQuestion.DoesNotExist:
        messages.error(request, "Given question does not exist")
        return redirect('dailyQuiz:list_questions')
    
    # Deletes the given question, and returns a success message as an indicator
    question.delete()
    messages.success(request, "Quiz question successfully deleted!")
    return redirect('dailyQuiz:list_questions')
    

# Creates and displays 10 randomly selected quiz questons for a player
@login_required
def get_daily_quiz(request):
    # Ensures only a player can do a daily quiz
    if request.user.role != 'player':
        messages.error(request, "You must be a Player to access this page.")    
        return redirect('dailyQuiz:quiz_home')
    
    # Checks if there has been an attempt previously on the same day, to prevent people rerolling questions
    quiz_attempt = QuizAttempt.objects.filter(user=request.user, date=timezone.now().date()).first()

    if quiz_attempt != None:
        # Uses the same questions from the same day quiz attempt
        questions = quiz_attempt.questions.all()

        if quiz_attempt.is_submitted == True: # chnage this to true in final build
            messages.error(request, "You have already submitted a quiz today. Please come back tomorrow for another!")    
            return redirect('dailyQuiz:quiz_home')

    else:
        # Generate a new quiz with 10 randomly selected unique questions
        questions = random.sample(list(QuizQuestion.objects.all()), 10)

        # Stores the new quiz attempt
        quiz_attempt = QuizAttempt.objects.create(user=request.user)
        quiz_attempt.questions.set(questions)

    context = {'questions': questions}
    return render(request, 'dailyQuiz/daily_quiz.html', context)

# Marks and scores the player's quiz when they press submit. Stores necessary data in the DB
@login_required
def submit_quiz(request):
    if request.user.role != 'player':
         messages.error(request, "You must be a Player to access this page.")    
         return redirect('dailyQuiz:quiz_home')

    if request.method == "POST":
        # Get today's quiz attempt. If no attempt today, redirects to get daily quiz page
        quiz_attempt = QuizAttempt.objects.filter(user=request.user, date=timezone.now().date()).first()
        if quiz_attempt == None:
            return redirect('dailyQuiz:quiz')
        # If quiz attempt is_submitted attribute equal to True, redirects user away, and informs them they already did a quiz today
        elif quiz_attempt.is_submitted == True: # change this to true in final build 
            messages.error(request, "You have already submitted a quiz today. Please come back tomorrow for another!")    
            return redirect('dailyQuiz:quiz_home')
        
        score = 0
        results = []

        # Retrieves all questions for user's quiz
        questions = quiz_attempt.questions.all()

        # Loops through every question submitted by user and tallies score
        for question in questions:
            user_answer = request.POST.get(f"{question.id}")
            
            # Ensures user has answered every question
            if user_answer == None:
                messages.error(request, "You must answer all questions before submitting.")
                return redirect("dailyQuiz:quiz")

            # If user's answer to question is correct, increase score by 1
            if user_answer == question.correct_option:
                score += 1
                results.append({'question':question, 'correct': True})
            else:
                results.append({'question':question, 'correct': False})


        # Saves final score to the quiz attempt record, and sets is_submitted to true
        quiz_attempt.score = score
        quiz_attempt.is_submitted = True
        quiz_attempt.save()

    
        streak, created = QuizDailyStreak.objects.get_or_create(user=request.user)
       


        # If score is 8 or more, increase streak by 1. Else reset streak
        if score >= 8:
            streak.current_streak += 1
        else: 
            streak.current_streak = 0

        # Updates user's streak
        streak.last_completed_quiz_date = timezone.now().date()
        streak.save()

        context = {"score": score, "streak": streak.current_streak, "results": results}
        return render(request, "dailyQuiz/result.html", context)
    


def quiz_result_view(request):
    # Get the current user
    user = request.user

    # Fetch the user's streak (if it exists)
    try:
        streak = QuizDailyStreak.objects.get(user=user).current_streak
    except QuizDailyStreak.DoesNotExist:
        streak = 0  # Default value if no streak exists

    # Pass the streak to the template
    return render(request, 'quiz_result.html', {
        'streak': streak,
        # Add other context variables as needed
    })
    
    
    