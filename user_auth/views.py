from django.shortcuts import render
from django.shortcuts import render,redirect
from .forms import SignupForm
from django.contrib.auth import login,logout,authenticate
from .models import User
from django.contrib import messages
from datetime import datetime,timedelta
from django.contrib.auth.hashers import make_password
from home.views import index
from django.core.mail import send_mail
from .utils import send_otp
import pyotp

# Create your views here.

def sign_up(request):
    form = SignupForm()
    if request.POST:
        form = SignupForm(request.POST)
        if form.is_valid():
            request.session['email']=form.cleaned_data.get('email')
            request.session['username']=form.cleaned_data.get('username')
            request.session['first_name']=form.cleaned_data.get('first_name')
            request.session['last_name']=form.cleaned_data.get('last_name')
            request.session['password']=form.cleaned_data.get('password')

            send_otp(request)
            return redirect(otp_view)
    context = {'form' : form}
    return render(request, 'user_auth/user_signup.html', context)

def log_in(request):
    if request.POST:
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(email=email, password=password)
        if user is not None:
            if hasattr(user, 'is_block') and user.is_block: 
                messages.error(request, 'Your account is blocked. Please contact support.')
            elif not user.is_block: 
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'Invalid username or password')
        else:
            messages.error(request, 'Invalid username or password')
        

    return render(request, 'user_auth/user_login.html')

def otp_view(request):
    if request.POST:
        otp = request.POST['otp']

        otp_secret_key = request.session['otp_secret_key']
        otp_valid_date = request.session['otp_valid_date']

        if otp_secret_key and otp_valid_date is not None:
            valid_until = datetime.fromisoformat(otp_valid_date)
            if valid_until > datetime.now():
                totp = pyotp.TOTP(otp_secret_key, interval=60)
                if totp.verify(otp):
                    encrypted_password = make_password(request.session['password'])
                    user = User(
                    username=request.session['username'],
                    email=request.session['email'],
                    password=encrypted_password,
                    first_name=request.session.get("first_name"),
                    last_name=request.session.get("last_name"),
                    )
                    user.save()
                    messages.success(request, 'OTP successfully verified. Your account has been created')
                    del request.session['otp_secret_key']
                    del request.session['otp_secret_key']
                    return redirect(log_in)
                else:
                    messages.error(request, 'Incorrect OTP. Please double-check and try again.')
            else:
                messages.error(request, 'OTP has expired. Please request a new OTP.')
        else:
            messages.error(request, 'An unexpected error occurred during OTP verification. Please try again later.')

    return render(request, 'user_auth/otp.html')

def resend_otp(request):
    send_otp(request)
    return redirect(otp_view)


def forgot_password(request):
    return render(request, 'forgot_password.html')
            


def log_out(request):
    logout(request)
    return redirect(index)