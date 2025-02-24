
# social/admin.py
from django.contrib import admin
from .models import Announcement
# Register your models here.
@admin.register(Announcement)

class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at')  # Customize the fields to display
    search_fields = ('title', 'summary', 'content')  # Make the title and content searchable


