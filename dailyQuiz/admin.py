from django.contrib import admin
from .models import QuizQuestion, QuizAttempt, QuizDailyStreak

# Register your models here.


class QuizQuestionAdmin(admin.ModelAdmin):
    # Fields to display in the list view
    list_display = ('id', 'question', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option')
    
    # Fields that can be edited directly in the list view
    list_editable = ('question', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option')
    list_display_links = ('id',)  # Use 'id' as the link to the edit page

    # Add search functionality
    search_fields = ('question',)

    # Add filters for the correct_option field
    list_filter = ('correct_option',)


class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'score', 'date', 'is_submitted')

class QuizDailyStreakAdmin(admin.ModelAdmin):
    list_display = ('user', 'current_streak', 'last_completed_quiz_date')


admin.site.register(QuizQuestion, QuizQuestionAdmin)
admin.site.register(QuizAttempt, QuizAttemptAdmin)
admin.site.register(QuizDailyStreak, QuizDailyStreakAdmin)