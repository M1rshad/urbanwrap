from django import forms
from django.contrib.auth.forms import UserCreationForm
from user_auth.models import User, UserProfile


class SignupForm(UserCreationForm):

    class Meta:
        model = User
        fields = ['username', 'email','first_name','last_name']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('dp', 'bio')