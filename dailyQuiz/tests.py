from django.test import TestCase
from accounts.models import CustomUser
from django.urls import reverse
from .models import QuizAttempt, QuizDailyStreak, QuizQuestion
from shop.models import UserBalance
from .tasks import reset_daily_streak
from django.utils.timezone import now, timedelta

# Create your tests here.
class SetUpTest(TestCase):
    def setUp(self):
        # Contains most of the urls used
        self.home_page_url = reverse('dailyQuiz:quiz_home')
        self.list_questions_url = reverse('dailyQuiz:list_questions')
        self.create_question_url = reverse('dailyQuiz:create_question')
        self.quiz_url = reverse('dailyQuiz:quiz')
        self.submit_quiz_url = reverse('dailyQuiz:submit_quiz')

        # Creates a test player account
        self.player = CustomUser.objects.create_user(email ='player@gmail.com', 
                                                    username = 'player1', 
                                                    password = 'testpassword12345',
                                                    first_name = 'Player',
                                                    last_name = 'User',
                                                    role = 'player',
                                                    verified = True)
        
        # Creates a quiz daily streak for test player account
        self.player_streak = QuizDailyStreak.objects.create(user=self.player, last_completed_quiz_date=now().date() - timedelta(days=1) , current_streak=5)

        self.player_balance = UserBalance.objects.create(user_id=self.player, currency=20)

        # Creates a test game keeper account
        self.game_keeper = CustomUser.objects.create_user(email ='gamekeeper@gmail.com', 
                                                         username = 'gamekeeper1', 
                                                         password = 'testpassword54321',
                                                         first_name = 'Game',
                                                         last_name = 'Keeper',
                                                         role = 'gameKeeper',
                                                         is_staff = True,
                                                         verified = True)
        
        # Creates 10 daily quiz questions
        self.questions = [
            QuizQuestion.objects.create(
                question=f"Test Question {i + 1}",
                option_a="A",
                option_b="B",
                option_c="C",
                option_d="D",
                correct_option="option_b" 
            ) for i in range(10) 
        ]
        

class ListQuestionTest(SetUpTest):
    def test_game_keeper_can_access_list_question_page(self):
        """Verifies a game keeper can access the page"""
        self.client.login(username="gamekeeper1", password="testpassword54321")
        response = self.client.get(self.list_questions_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dailyQuiz/list_questions.html')

    def test_player_cant_access_list_question_page(self):
        """Verifies a player is redirected when trying to access the page"""
        self.client.login(username="player1", password="testpassword12345")
        response = self.client.get(self.list_questions_url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.home_page_url)

    def test_page_displays_all_questions(self):
        """Verifies all questions created in setup are displayed"""
        self.client.login(username="gamekeeper1", password="testpassword54321")
        response = self.client.get(self.list_questions_url)

        # Ensures that the correct page is being checked
        self.assertTemplateUsed(response, 'dailyQuiz/list_questions.html')

        # verifies that all 10 questions are on the page
        for question in self.questions:
            self.assertContains(response, question.question)

class CreateDeleteQuestionTest(SetUpTest):
    def test_game_keeper_can_access_create_question_page(self):
        """Verifies a game keeper can access create question page"""
        self.client.login(username="gamekeeper1", password="testpassword54321")
        response = self.client.get(self.create_question_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dailyQuiz/create_question.html')

    def test_player_cant_access_create_question_page(self):
        """Verifies a player is redirected when trying to access the create question page"""
        self.client.login(username="player1", password="testpassword12345")
        response = self.client.get(self.create_question_url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.home_page_url)

    def test_can_create_quiz_question(self):
        """Verifies a game keeper can create a question, and it changes the DB in the expected ways"""
        self.client.login(username="gamekeeper1", password="testpassword54321")
        
        # Verifies how many questions there are in the DB before creation
        self.assertEqual(QuizQuestion.objects.count(), 10)

        valid_question = {
            'question': '2 + 2',
            'option_a': '1',
            'option_b': '2',
            'option_c': '3',
            'option_d': '4',
            'correct_option': 'option_d'
        }

        # Verifies the user is redirected back to the list question page after question creation
        response = self.client.post(self.create_question_url, valid_question)
        self.assertRedirects(response, self.list_questions_url)

        # Verifies the question is in the DB
        self.assertTrue(QuizQuestion.objects.filter(question='2 + 2').exists()) 
        self.assertEqual(QuizQuestion.objects.count(), 11)

    def test_can_delete_quiz_question(self):
        """Verifies a gamekeeper can delete a question"""
        self.client.login(username="gamekeeper1", password="testpassword54321")

        # Verifies the question to be deleted exists before deletion
        self.assertTrue(QuizQuestion.objects.filter(id=1).exists())

        response = self.client.post(reverse('dailyQuiz:delete_question', args=[1]))

        # Verifies the player is redirected back to the list questions page, and the question no longer exists in DB
        self.assertRedirects(response, self.list_questions_url)
        self.assertFalse(QuizQuestion.objects.filter(id=1).exists())

class QuizTest(SetUpTest):
    def test_player_can_access_daily_quiz_and_see_questions(self):
        """Verifies a player can access the daily quiz page, and see the questions in the DB"""
        self.client.login(username="player1", password="testpassword12345")
        response = self.client.get(self.quiz_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dailyQuiz/daily_quiz.html')
        self.assertEqual(len(response.context['questions']), 10)
        for question in self.questions:
            self.assertContains(response, question.question)

    def test_game_keeper_cant_access(self):
        """Verifies game keeper cant access the get quiz page"""
        self.client.login(username="gamekeeper1", password="testpassword54321")
        response = self.client.get(self.quiz_url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.home_page_url)

    def test_submit_quiz_with_correct_answers(self):
        """Verifies a player can submit answers to the quiz, and it affects the DB in the expected way"""
        self.client.login(username="player1", password="testpassword12345")
        
        quiz_attempt = QuizAttempt.objects.create(user=self.player)
        quiz_attempt.questions.set(self.questions)

        # Creates a dictionary with all questions answer correctly, and uses it for the view
        answers = {f"{i}": "option_b" for i in range(1, 11)}
        response = self.client.post(self.submit_quiz_url, answers)

        # Verifies the player renders the correct page
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dailyQuiz/result.html')

        # Verifies the player's quiz attempt has the correct score
        quiz_attempt.refresh_from_db()
        self.assertEqual(quiz_attempt.score, 10)
        self.assertTrue(quiz_attempt.is_submitted)

        # Verifies the html page displays the players score, and current streak
        self.assertContains(response, "Final Score: 10 / 10")
        self.assertContains(response, "Current streak: 6 days")

        # Verifies the player's daily streak is updated correctly 
        self.player_streak.refresh_from_db()
        self.assertEqual(self.player_streak.current_streak, 6)

    def test_submit_quiz_with_incorrect_answers(self):
        """Verifies a player can submit wrong answers to the quiz, and it affects the DB in the expected way"""
        self.client.login(username="player1", password="testpassword12345")

        # Creates quiz attempt with the test questions and player
        quiz_attempt = QuizAttempt.objects.create(user=self.player)
        quiz_attempt.questions.set(self.questions)

        # Creates a dictionary with all questions answer incorrectly, and uses it for the view
        answers = {f"{i}": "option_a" for i in range(1, 11)}
        response = self.client.post(self.submit_quiz_url, answers)

        # Verifies the player renders the correct page
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dailyQuiz/result.html')

        # Verifies the player's quiz attempt has the correct score
        quiz_attempt.refresh_from_db()
        self.assertEqual(quiz_attempt.score, 0)
        self.assertTrue(quiz_attempt.is_submitted)

        # Verifies the html page displays the players score, and displays the correct message for scoring below 8
        self.assertContains(response, "Final Score: 0 / 10")
        self.assertContains(response, "Unfortunately, your daily streak has been reset as you scored less than 8 on today's quiz.")

        # Verifies the player's daily streak is updated correctly 
        self.player_streak.refresh_from_db()
        self.assertEqual(self.player_streak.current_streak, 0)

    def test_submit_quiz_with_half_questions_answered(self):
        """Verifies a player cant submit answers to the quiz, without answering all questions"""
        self.client.login(username="player1", password="testpassword12345")

        # Creates quiz attempt with the test questions and player
        quiz_attempt = QuizAttempt.objects.create(user=self.player)
        quiz_attempt.questions.set(self.questions)

        # Creates a dictionary with with half the questions answer correctly, and other half left empty
        answers = {f"{i}": "option_b" for i in range(1, 6)}
        response = self.client.post(self.submit_quiz_url, answers)

        # Verifies the player is redirected to the correct page
        self.assertRedirects(response, self.quiz_url)  

class DailyStreakResetTest(SetUpTest):
    def test_player_streak_doesnt_reset_if_last_completed_quiz_yesterday(self):
        """Verifies the player's daily streak isnt reset if they completed a quiz yesterday"""
        reset_daily_streak.apply()
        self.player_streak.refresh_from_db()

        self.assertEqual(self.player_streak.current_streak, 5)

    def test_player_streak_reset_for_last_completed_quiz_before_yesterday(self):
        """Verifies the player's daily streak is reset if they havent completed a quiz yesterday"""
        self.player_streak.last_completed_quiz_date = now().date() - timedelta(days=2)
        self.player_streak.save()

        reset_daily_streak.apply()
        self.player_streak.refresh_from_db()

        self.assertEqual(self.player_streak.current_streak, 0)