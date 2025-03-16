from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, update_session_auth_hash, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import render, redirect
from django.urls import reverse
from shop.models import UserBalance
from leaderboards.models import TreeScore
from .forms import ProfileImageForm, SignUpForm, LoginForm, ChangeUsernameForm
from .models import Profile, CustomUser
from dailyQuiz.models import QuizDailyStreak



def signup_page(request):
    """Allows new users to create accounts. This view handles user registration through 
       the sign up page's form."""
    if request.user.is_authenticated:
        return redirect('main:map')

    form = SignUpForm()

    # If a form is submitted, the following happens
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            send_email_verification(request, user)
            messages.success(request, "You have successfully created a new account, please check your email for a verification link!")
            return redirect('accounts:login')
    

    context = {'form': form}
    return render(request, 'accounts/signup.html', context)



def send_email_verification(request, user: CustomUser) -> None:
    """Sends an verification email link to the new user"""
    subject = "Email Verification for Sustainable Campus"
    link = request.build_absolute_uri(reverse('accounts:email_verification', args=[user.verification_token]))
    message = f"Hello {user.first_name}, \n\nPlease verify your email through the following link below:\n{link}\n\nThank You!"
    sender = settings.EMAIL_HOST_USER  # Sender of email is stored in settings.py
    receiver = [user.email]
    
    send_mail(subject, message, sender, receiver)



def email_verification(request, token: str):
    """Handles email verification when the verification link is clicked for a new account"""

    # Retrieves user data using given verification token, returns error message if invalid
    try:
        user = CustomUser.objects.get(verification_token=token)
    except CustomUser.DoesNotExist:
        messages.error(request, "Invalid or expired verification token")
        return redirect('accounts:signup')

    # Verifies the user if the token matches an account
    if user.verified == False:
        user.verified = True
        user.save()

        # Creates a user balance for player
        UserBalance.objects.create(user_id=user)

        # Creates a score counter for the tree game for player
        TreeScore.objects.create(user=user)


        QuizDailyStreak.objects.create(user=user)
  
        messages.success(request, "Your account has now been verified, you can now log in.")
    else:
        messages.error(request, "This account has already been verified.")

    return redirect('accounts:login')



def login_page(request):
    """Allows users to login into the website. Handles user login through the login page's form."""

    # Redirect users who have already logged in
    if request.user.is_authenticated:
        return redirect('main:map')  

    form = LoginForm(request)

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")

            user = authenticate(request, username=username, password=password)

            if user is not None:
                if user.verified:
                    login(request, user)
                    return redirect('main:map')
                else:
                    messages.error(request, 'Your account has not been verified.')
            else:
                messages.error(request, 'Invalid username or password')
        else:
            messages.error(request, 'Invalid username or password')

    context = {'form': form}
    return render(request, 'accounts/login.html', context)


def logout_view(request):
    """Used for logging users out"""
    logout(request)
    messages.success(request, "Log out successfully")
    return redirect("accounts:login")


@login_required
def profile_page(request):
    """Displays info about a users profile"""
    # Ensure user has a profile
    if not hasattr(request.user, 'profile'):
        Profile.objects.create(user=request.user)

    # Initialized context
    context = {
        'username': request.user.username,
        'email': request.user.email,
        'form': PasswordChangeForm(request.user),
        'form_image': ProfileImageForm(instance=request.user.profile)
    }

    # For test: print(f"DEBUG - Current User: {request.user.username}")
    return render(request, 'accounts/profile.html', context)


@login_required
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


@login_required
def change_password(request):
    """
    Handles password change requests for authenticated users. Uses Django's form validation
    to ensure new password meets security requirements. Maintains user session after password
    change by updating auth hash.
    """
    base_context = {
        'username': request.user.username,
        'email': request.user.email,
        'form': PasswordChangeForm(request.user)
    }

    if request.method == 'POST':
        # Initialize password change form with user and POST data
        form = PasswordChangeForm(request.user, request.POST)
        # Validate form data
        if form.is_valid():
            # Save new password
            user = form.save()
            # Maintain session continuity after password change
            update_session_auth_hash(request, user)
            # Set success notification
            messages.success(request, 'Your password has been updated successfully!')
            # Redirect to profile page
            return redirect('accounts:profile')
        else:
            base_context.update({
                'form': form,
                'username': request.user.username,
                'email': request.user.email
            })
            # Set error notification for invalid form
            messages.error(request, 'Please correct the errors below.')
            return render(request, 'accounts/profile.html', base_context)

    else:
        # Initialize empty form for GET requests
        form = PasswordChangeForm(request.user)
    # Render password change template with form context
    return render(request, 'accounts/profile.html', base_context)


def password_reset(request):
    form = SignUpForm()

    # If a form is submitted, the following happens
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            # Checks if given email is unique before saving new user data
            if CustomUser.objects.filter(email=form.cleaned_data["email"]).exists():
                form.add_error("email", "Email is already in use.")
            # Saves new user data, and sends email verification
            else:
                user = form.save()
                send_email_verification(user)
                return redirect('accounts:login')

    context = {'form': form}
    return render(request, 'accounts/signup.html', context)


@login_required
def change_profile_image(request):
    if request.method == 'POST':
        form = ProfileImageForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            profile = form.save(commit=False)
            print("Uploaded file: ", request.FILES['image'])  # print uploaded file
            form.save()
            return redirect('accounts:profile')
    else:
        form = ProfileImageForm()

    return render(request, 'accounts/change_profile_image.html', {'form': form})


@login_required
def delete_account(request):
    if request.method == 'POST':
        try:
            user = request.user
            password = request.POST.get('delete_password', '')

            if not user.check_password(password):
                messages.error(request, '密码验证失败')
                return redirect('accounts:profile')

            # 手动清理所有可能关联数据
            with transaction.atomic():
                # 清理用户点赞记录
                # if 'announcements' in settings.INSTALLED_APPS:
                #     from announcements.models import Announcement
                    # Announcement.objects.filter(likes=user).update(likes=user)
                    # user.liked_announcements.clear()

                # 清理其他关联数据
                UserBalance.objects.filter(user_id=user).delete()
                TreeScore.objects.filter(user=user).delete()

                # 执行登出
                logout(request)

                # 删除用户
                user.delete()

            messages.success(request, '账号已永久删除')
            return redirect('accounts:login')

        except Exception as e:
            messages.error(request, f'删除失败: {str(e)}')
            return redirect('accounts:profile')

    return redirect('accounts:profile')

