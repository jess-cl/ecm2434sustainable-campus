from django.urls import path
from . import views

app_name = 'dailyQuiz'

urlpatterns = [
    path('', views.quiz_home, name="quiz_home"),
    path("list-questions/", views.list_quiz_questions, name="list_questions"),
    path("create-question/", views.create_quiz_question, name="create_question"),
    path("delete-question/<int:question_id>/", views.delete_quiz_question, name="delete_question"),
    path("quiz/", views.get_daily_quiz, name="quiz"),
    path("submit-quiz/", views.submit_quiz, name="submit_quiz"),
]