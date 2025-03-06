from django.contrib import admin
from .models import Announcement, Event, EventAttended
# Register your models here.
@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at')  # Fields to display
   # list_editable = ('created_at',)  # Make created_at editable
    search_fields = ('title', 'summary', 'content')  # Make the title and content searchable

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('announcement', 'event_date', 'currency_reward', 'event_code')  # Fields displayed in list view
    search_fields = ('announcement__title', 'event_code')  # Allows searching by title or event code

@admin.register(EventAttended)
class EventAttendedAdmin(admin.ModelAdmin):
    list_display = ('player', 'event')  # Shows player and event attended
    search_fields = ('player__username', 'event__event_code')
