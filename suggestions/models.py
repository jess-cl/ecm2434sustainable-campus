from django.db import models
from django.conf import settings
from django.db import models
class Suggestion(models.Model):
    """Represents suggestions made by users"""
    CATEGORY_CHOICES = [
        ('location', 'Add a location'),
        ('bug', 'Bug report'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
