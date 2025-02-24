from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, update_session_auth_hash
from .forms import SignUpForm, LoginForm, ChangeUsernameForm
from django.contrib.auth import logout
from django.core.mail import send_mail
from django.conf import settings
from .models import CustomUser
from shop.models import UserBalance


# Handles data submitted from signup page's form
def signup_page(request):
    # If a form is submitted, the following happens
    if request.method == 'POST':
        form = SignUpForm(request.POST)

        # If form is valid, saves new user data, and sends email verification
        if form.is_valid():
            user = form.save()
            send_email_verification(user)
            return redirect('accounts:login')
        else:
            return render(request, 'accounts/signup.html', {'form': form})

    else:
        form = SignUpForm()


    return render(request, 'accounts/signup.html', {'form': form})


# Sends an verification email with a link to the new user
def send_email_verification(user):
    subject = "Email Verification for Sustainable Campus"
    link = f"http://127.0.0.1:8000/accounts/email_verification/{user.verification_token}"
    message = f"Hello {user.first_name}, \n\nPlease verify your email through the following link below:\n{link}\n\nThank You!"
    sender = settings.EMAIL_HOST_USER  # Sender of email is stored in settings.py
    receiver = [user.email]

    send_mail(subject, message, sender, receiver)


# Determines what happens when the verification link is clicked
def email_verification(request, token):
    # Retrieves user data using given verification token, returns error if invalid
    try:
        user = CustomUser.objects.get(verification_token=token)
    except CustomUser.DoesNotExist:
        messages.error(request, "Invalid or expired verification token")
        return redirect('accounts:login')

    # Verifies user if they are unverified, and creates user balance for account
    if user.verified == False:
        user.verified = True
        user.save()

        UserBalance.objects.create(user_id=user)

        messages.success(request, "User has now been verified, you can now log in.")
    else:
        messages.error(request, "User is already verified")

    return redirect('accounts:login')


# Handles data submitted by login page's form
def login_page(request):
    form = LoginForm(request)

    # If a form is submitted, the following happens
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            # Retrieves username and password from submitted form
            username = request.POST.get("username")
            password = request.POST.get("password")

            # Retrieves user data for matching username and password
            user = authenticate(request, username=username, password=password)

            # Checks if user data has been retrieved
            if user is not None:
                # Checks if user is verified
                if user.verified == True:
                    login(request, user)
                    return redirect('main:map')

                else:
                    form.add_error(None, 'Email has not been verified')

            else:
                form.add_error(None, 'Invalid username or password')

        else:
            context = {'form': form}
            return render(request, 'accounts/login.html', context)

    context = {'form': form}
    return render(request, 'accounts/login.html', context)


def logout_view(request):
    logout(request)
    messages.success(request, "Log out successfully")
    return redirect("accounts:login")


@login_required  # Make sure the user is logged in
def profile_page(request):
    username = request.user.username
    email = request.user.email
    context = {
        'username': username,
        'email': email,
    }
    return render(request, 'accounts/profile.html', context)


def change_username(request):
    """
    This function processes POST requests when the user submits a new username through the form. If the request method is POST and the form data is valid,
    it updates the user's username and redirects to the profile page. If the data is invalid, it reloads the profile page with the current form errors.
    If the request method is not POST, it loads the username change form with the current user information.
    """
    if request.method == 'POST':
        # Create a form instance with the submitted data and the current user instance
        form = ChangeUsernameForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Username modification was successful!")
            return redirect('accounts:profile')
        else:
            return render(request, 'accounts/profile.html', {
            'form': form,  # Form containing error message
            'show_modal': True
        })
    else:
        # If not a POST request, create a blank form instance with the current user information
        form = ChangeUsernameForm(instance=request.user)

    # Render the profile page with the username change form
    return render(request, 'accounts/profile.html', {
        'form': form,
        'show_modal': False
    })


def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password has been updated successfully!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'accounts/change_password.html', {'form': form})
