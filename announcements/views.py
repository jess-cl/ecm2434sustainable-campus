import string, random, qrcode, os

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from datetime import date
from shop.models import UserBalance, CurrencyTransaction

from .forms import AnnouncementForm
from .models import Announcement, Event, EventAttended

@login_required
def announcement_list(request):
    """Displays all announcements made by game keepers and developers. Supplies optional filters."""
    announcements = Announcement.objects.all().order_by('-created_at')
    
    author = request.GET.get('author')
    role = request.GET.get('role')
    date = request.GET.get('date')
    sort = request.GET.get('sort')
    
    # Apply filters
    if author:
        announcements = announcements.filter(author__username__icontains=author)
    if role:
        announcements = announcements.filter(author__role__icontains=role)
    if date:
        announcements = announcements.filter(created_at__date=date)
    
    # Apply sorting
    if sort == "newest":
        announcements = announcements.order_by('-created_at')  # Newest first
    elif sort == "oldest":
        announcements = announcements.order_by('created_at')   # Oldest first

    context={'announcements': announcements, 'user_role': request.user.role}
    return render(request, 'announcements/announcement_list.html', context)

@login_required
def create_announcement(request):
    """Allows game keepers and developers to create announcements to be displayed in the announcement list"""

    # Ensures only a game keeper or developer can create an announcement
    if request.user.role == 'player':  
        messages.error(request, "You must be a Game Keeper to access this page.")    
        return redirect('/announcements/')
    
    if request.method == 'POST': # posts the announcement
        form = AnnouncementForm(request.POST, request.FILES)
        if form.is_valid():
            new_announcement = form.save(commit=False)
            new_announcement.author = request.user
            new_announcement.save()

            # Creates a event record if is_event is true on announcement form
            if form.cleaned_data.get('is_event') == True:
                currency_reward = form.cleaned_data.get('currency_reward')
                transaction_description = form.cleaned_data.get('transaction_description')
                event_date = form.cleaned_data.get('event_date')
                event_code = event_code_generator()

                Event.objects.create(
                    announcement=new_announcement, 
                    currency_reward=currency_reward, 
                    transaction_description=transaction_description, 
                    event_date=event_date, 
                    event_code=event_code
                )

        messages.success(request, "New announcement created successfully.")
        return redirect('announcements:announcement_list')
    
    
    form = AnnouncementForm()
    context = {'form': form}
    return render(request, 'announcements/create_announcement.html', context)


def event_code_generator(size=32, chars=string.ascii_uppercase + string.digits):
    """Function used for generating a unique 32-character event code."""
    while True:
        event_code = ''.join(random.choice(chars) for _ in range(size))
        if Event.objects.filter(event_code=event_code).exists() == False:
            return event_code


@login_required 
def display_event_qr_code(request, event_code):
    """View used by game keepers to generate and display a QR code for event attendance verification"""

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
    qr_code = qrcode.make(redeem_url)

    # Creates qr_code image using url, and saves it in media/qr_codes folder
    qr_code_folderpath = os.path.join(settings.MEDIA_ROOT, 'qr_codes/')
    qr_code_name = f"{event_code}.jpg"
    qr_code_filepath = os.path.join(qr_code_folderpath, qr_code_name)
    qr_code.save(qr_code_filepath)

    # Sends the location of qr_code and event data to the html page
    qr_code_url = f"{settings.MEDIA_URL}qr_codes/{qr_code_name}"
    context = {'qr_code':qr_code_url, 'event':event}
    return render(request, 'announcements/display_event_qr_code.html', context)


@login_required 
def redeem_event_reward(request, event_code):
    """Used for allowing players to verifiy they attended an event, and be given a reward."""

    # Verifies the user is a player
    if request.user.role != 'player':
        messages.error(request, "User must be a player to redeem event rewards.")
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
    
    # Registers the player attendance of the event, and rewards them
    EventAttended.objects.create(player=request.user, event=event)
    user_balance = get_object_or_404(UserBalance, user_id=request.user)
    user_balance.currency = user_balance.currency + event.currency_reward
    user_balance.save()

    # Create a currency transaction, that states the amount of currency the player is given
    CurrencyTransaction.objects.create(
        user=request.user, 
        currency_difference=event.currency_reward, 
        description=event.transaction_description)

    messages.success(request, f"You attended {event.announcement}, and received {event.currency_reward} currency")
    return redirect('announcements:announcement_list')

@login_required
def like_announcement(request, announcement_id):
    """Allows a user to like an announcement."""
    announcement = get_object_or_404(Announcement, id=announcement_id)
    user = request.user

    if user in announcement.likes.all():
        announcement.likes.remove(user)  # Unlike the announcement
    else:
        announcement.likes.add(user)  # Like the announcement
        announcement.dislikes.remove(user)  # Remove like if the user had liked it

    return redirect('/announcements/', announcement_id=announcement.id)  # Redirect to the announcement detail page

@login_required
def dislike_announcement(request, announcement_id):
    """Allows a user to like an announcement."""
    announcement = get_object_or_404(Announcement, id=announcement_id)
    user = request.user

    if user in announcement.dislikes.all():
        announcement.dislikes.remove(user)  # Remove dislike
    else:
        announcement.dislikes.add(user)  # Add dislike
        announcement.likes.remove(user)  # Remove like if the user had liked it

    return redirect('/announcements/', announcement_id=announcement.id)

