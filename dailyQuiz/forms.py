from django import forms
from .models import QuizQuestion

class QuizQuestionForm(forms.ModelForm):
    class Meta:
        model = QuizQuestion
        fields = ['question', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option']

    OPTION_CHOICES = [
        ('option_a', 'Option A'),
        ('option_b', 'Option B'),
        ('option_c', 'Option C'),
        ('option_d', 'Option D'),
    ]

    correct_option = forms.ChoiceField(choices=OPTION_CHOICES)