from django.core.validators import MaxValueValidator, MinValueValidator
# models.py

from django.db import models  
from django.contrib.auth.models import User  

class Announcement(models.Model):
    """Represents announcements made by game keepers or developers"""
    title = models.CharField(max_length=200)
    summary = models.TextField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='announcement_images/', null=True, blank=True)  # Image field
    is_event = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
    likes = models.ManyToManyField('accounts.CustomUser', related_name='liked_announcements', blank=True)  # Many-to-many relationship for likes
    dislikes = models.ManyToManyField('accounts.CustomUser', related_name='disliked_announcements', blank=True) 

    def __str__(self):
        return self.title

    def get_author_role(self):
        return self.author.role  
      
    def total_likes(self):
        return self.likes.count()

    
class Event(models.Model):
    """Represents events to occur, and attached to events"""
    announcement = models.OneToOneField(Announcement, on_delete=models.CASCADE)
    currency_reward = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(300)])
    transaction_description = models.TextField(max_length=200)
    event_date = models.DateField()
    event_code = models.TextField(max_length=32)


class EventAttended(models.Model):
    """Represents events that players attend"""
    player = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

