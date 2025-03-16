from django.db import models

# Create your models here.
class QuizQuestion(models.Model):
    OPTION_CHOICES = [
        ('option_a', 'Option A'),
        ('option_b', 'Option B'),
        ('option_c', 'Option C'),
        ('option_d', 'Option D'),
    ]

    question = models.TextField()
    option_a = models.CharField(max_length=255, blank=True, null=True)
    option_b = models.CharField(max_length=255, blank=True, null=True)
    option_c = models.CharField(max_length=255, blank=True, null=True)
    option_d = models.CharField(max_length=255, blank=True, null=True)
    correct_option = models.CharField(choices=OPTION_CHOICES, max_length=10)

class QuizAttempt(models.Model):
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
    questions = models.ManyToManyField(QuizQuestion) 
    score = models.IntegerField(default=0)
    date = models.DateField(auto_now_add=True)
    is_submitted = models.BooleanField(default=False)

class QuizDailyStreak(models.Model):
    user = models.OneToOneField('accounts.CustomUser', on_delete=models.CASCADE)
    current_streak = models.IntegerField(default=0)
    last_completed_quiz_date = models.DateField(null=True, blank=True)