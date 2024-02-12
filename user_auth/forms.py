from django import forms
from django.contrib.auth.forms import UserCreationForm
from user_auth.models import User, UserProfile, ShippingAddress


class SignupForm(UserCreationForm):

    class Meta:
        model = User
        fields = ['username', 'email','first_name','last_name']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('dp', 'bio')


class ShippingAddressForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields =('first_name','last_name','phone','email','address_line_1','address_line_2','country','state','city','pin_code')