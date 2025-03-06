from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Announcement, Event, EventAttended
from shop.models import UserBalance, CurrencyTransaction
from .forms import AnnouncementForm
from django.contrib import messages
import string, random, qrcode
from django.conf import settings
import os
from datetime import date
from django.utils.timezone import now


def announcement_list(request):
    announcements = Announcement.objects.all()
    announcements = Announcement.objects.all().order_by('-created_at')

    # Get filter parameters from the request
    author = request.GET.get('author')
    role = request.GET.get('role')
    date = request.GET.get('date')

    # Apply filters
    if author:
        announcements = announcements.filter(author__username__icontains=author)
    if role:
        announcements = announcements.filter(author__role__icontains=role)
    if date:
        announcements = announcements.filter(created_at__date=date)

    return render(request, 'announcements/announcement_list.html', {'announcements': announcements})

@login_required
def create_announcement(request):
    if not request.user.is_authenticated: # makes sure user is logged in
        return redirect('accounts:login')  
    if request.user.role == 'player':  # makes sure user can't post if player role
        messages.error(request, "You must be a Game Keeper to access this page.")    
        return redirect('announcements:announcements')
    if request.method == 'POST': # posts the announcement
        form = AnnouncementForm(request.POST, request.FILES)
        if form.is_valid():
            new_announcement = form.save(commit=False)
            new_announcement.author = request.user
            new_announcement.save()
            if form.cleaned_data.get('is_event') == True:
                currency_reward = form.cleaned_data.get('currency_reward')
                transaction_description = form.cleaned_data.get('transaction_description')
                event_date = form.cleaned_data.get('event_date')
                event_code = event_code_generator()

                Event.objects.create(announcement=new_announcement, currency_reward=currency_reward, transaction_description=transaction_description, event_date=event_date, event_code=event_code)
            
            
            return redirect('announcements:announcement_list')
    else:
        form = AnnouncementForm()

    return render(request, 'announcements/create_announcement.html', {'form': form})

# Function used for generating 32 figure event code.
def event_code_generator(size=32, chars=string.ascii_uppercase + string.digits):
    while True:
        event_code = ''.join(random.choice(chars) for _ in range(size))
        if Event.objects.filter(event_code=event_code).exists() == False:
            return event_code

@login_required
def like_announcement(request, announcement_id):
    announcement = get_object_or_404(Announcement, id=announcement_id)
    user = request.user

    if user in announcement.likes.all():
        announcement.likes.remove(user)  # Unlike the announcement
    else:
        announcement.likes.add(user)  # Like the announcement
        announcement.dislikes.remove(user)  # Remove like if the user had liked it

    return redirect('/announcements/', announcement_id=announcement.id)  # Redirect to the announcement detail page

@login_required
def like_announcement(request, announcement_id):
    announcement = get_object_or_404(Announcement, id=announcement_id)
    user = request.user

    if user in announcement.likes.all():
        announcement.likes.remove(user)  # Unlike the announcement
    else:
        announcement.likes.add(user)  # Like the announcement
        announcement.dislikes.remove(user)  # Remove dislike if the user had disliked it

    # Redirect to the announcement list page
    return redirect('announcements:announcement_list')

@login_required
def dislike_announcement(request, announcement_id):
    announcement = get_object_or_404(Announcement, id=announcement_id)
    user = request.user

    if user in announcement.dislikes.all():
        announcement.dislikes.remove(user)  # Remove dislike
    else:
        announcement.dislikes.add(user)  # Add dislike
        announcement.likes.remove(user)  # Remove like if the user had liked it

    # Redirect to the announcement list page
    return redirect('announcements:announcement_list')
# View for display_event_code.html. Used to generate QR code for game keepers to display at events for 
# players to scan to be rewarded for attending. 
@login_required 
def display_event_qr_code(request, event_code):
    # Retrieves event with given event_code. If event does not exist, it involves user. 
    try:
        event = Event.objects.get(event_code=event_code)
    except Event.DoesNotExist:
        messages.error(request, "This event does not exist")
        return redirect('announcements:announcement_list')

    # Ensures the qr code can only be displayed by a game keeper or developer
    if request.user.role == 'player':
        messages.error(request, "You are not a gamekeeper or developer, you can not display this QR code.")
        return redirect('announcements:announcement_list')

    # Generates url for redeeming the reward for attending the event. 
    redeem_url = request.build_absolute_uri(reverse('announcements:redeem_event_reward', args=[event_code]))

    # Creates qr_code image using url, and saves it in media/qr_codes
    qr_code = qrcode.make(redeem_url)
    qr_code_folderpath = os.path.join(settings.MEDIA_ROOT, 'qr_codes/')
    qr_code_name = f"{event_code}.jpg"
    qr_code_filepath = os.path.join(qr_code_folderpath + qr_code_name)
    qr_code.save(qr_code_filepath)

    # Sends the location of qr_code and event data to html page
    qr_code_url = f"{settings.MEDIA_URL}qr_codes/{qr_code_name}"
    context = {'qr_code':qr_code_url, 'event':event}
    return render(request, 'announcements/display_event_qr_code.html', context)

# View for redeem_item.html. Used for redeeming items. 
@login_required 
def redeem_event_reward(request, event_code):
    # Ensures user has permissions
    if request.user.role != 'player':
        messages.error(request, "You are not a player, so you can not receive the event's reward")
        return redirect('announcements:announcement_list')

    # Checks if event exists, otherwise informs player that no event exists on given url. 
    try:
        event = Event.objects.get(event_code=event_code)
    except Event.DoesNotExist:
        messages.error(request, "There is no event with given code.")
        return redirect('announcements:announcement_list')

    # Ensures that scanning the event's QR code can only reward players on the day of the event
    today = date.today()
    if today < event.event_date:
        messages.error(request, f"You can only redeem event reward on day of the event. Please wait until {event.event_date}.")
        return redirect('announcements:announcement_list')
    elif today > event.event_date:
        messages.error(request, f"You can only redeem event reward on the day of the event, which is {event.event_date}. Event day has already passed.")
        return redirect('announcements:announcement_list')

    # Ensures player can not redeem the reward for the same event more than once. 
    if EventAttended.objects.filter(player=request.user, event__event_code=event_code).exists():
        messages.error(request, "You have already scanned this event's QR code, you can not do so again.")
        return redirect('announcements:announcement_list')
    
    # Creates record of player and the event they attended. Ensures player can't scan event reward QR code more than once
    EventAttended.objects.create(player=request.user, event=event)

    # Adds event reward to player's balance
    user_balance = get_object_or_404(UserBalance, user_id=request.user)
    user_balance.currency = user_balance.currency + event.currency_reward
    user_balance.save()

    # Create a currency transaction, that states the amount of currency the player is given
    CurrencyTransaction.objects.create(user=request.user, currency_difference=event.currency_reward, description=event.transaction_description)

    messages.success(request, f"You attended {event.announcement}, and received {event.currency_reward} currency")

    return redirect('announcements:announcement_list')
