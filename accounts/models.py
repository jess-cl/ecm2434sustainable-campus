from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

from django.conf import settings


# Create your models here.

# CustomUser inherits the functions and attributes of AbstactUser
class CustomUser(AbstractUser):
    """Represents a user's account"""
    # Ensures the role of player can only be one of three
    ROLES = [
        ('player', 'Player'),
        ('gameKeeper', 'Game Keeper'),
        ('developer', 'Developer'),
    ]

    # Additional custom attributes not inherited from AbstractUser
    role = models.CharField(max_length=50, choices=ROLES, default='player')
    verified = models.BooleanField(default=False)
    verification_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    creationDateTime = models.DateTimeField(auto_now_add=True)




class Profile(models.Model):
    """Represents a user profile settings"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='profile_images/', default='profile_images/default.png')

    def __str__(self):
        return f"{self.user.username}'s Profile"

