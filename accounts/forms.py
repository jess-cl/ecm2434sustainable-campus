from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, Profile
from .models import CustomUser



class SignUpForm(UserCreationForm):
    error_messages = {
        'password_mismatch': "The passwords you provided do not match. Please try again."
    }

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']


    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already in use, please use another email address.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already in use, please use another username.")
        return username


class LoginForm(AuthenticationForm):
    pass


#  Use ModelForm to simplify input
class ChangeUsernameForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username']

    # def clean_username(self):
    #     username = self.cleaned_data.get('username', '').strip()
    #
    #     if not username:
    #         raise forms.ValidationError("Username cannot be empty.")
    #     if len(username) < 3 or len(username) > 20:
    #         raise forms.ValidationError("The username must be between 3-20 characters.")
    #     if not re.match(r'^[a-zA-Z0-9_]+$', username):
    #         raise forms.ValidationError("Usernames can only contain letters, numbers, and underscores.")
    #     if CustomUser.objects.exclude(pk=self.instance.pk).filter(username=username).exists():
    #         raise forms.ValidationError("This username is already taken, please choose another one.")
    #
    #     return username


class ProfileImageForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control mb-2',
                'required': True,  #Forcefully adding the required attribute
                'accept': 'image/*'
            })
        }
