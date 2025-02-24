
# views.py

from django.shortcuts import render, redirect
from .models import Announcement
from .forms import AnnouncementForm
from django.contrib import messages

def announcement_list(request):
    announcements = Announcement.objects.all().order_by('-created_at')
    return render(request, 'announcements/announcement_list.html', {'announcements': announcements})


def create_announcement(request):


    if not request.user.is_authenticated: # makes sure user is logged in
        return redirect('/accounts/login/')  
    if request.user.role == 'player':  # makes sure user can't post if player role
        messages.error(request, "You must be a Game Keeper to access this page.")    
        return redirect('/announcements/')
    if request.method == 'POST': # posts the announcement
        form = AnnouncementForm(request.POST, request.FILES)
        if form.is_valid():
            new_announcement = form.save(commit=False)
            new_announcement.author = request.user
            new_announcement.save()
            return redirect('announcement_list')
    else:
        form = AnnouncementForm()
    return render(request, 'announcements/create_announcement.html', {'form': form})


