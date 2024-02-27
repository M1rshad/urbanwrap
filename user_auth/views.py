from django.shortcuts import render
from django.shortcuts import render,redirect
from .forms import SignupForm
from django.contrib.auth import login,logout,authenticate
from .models import User
from shop.models import Cart, CartItem
from django.contrib import messages
from datetime import datetime,timedelta
from django.contrib.auth.hashers import make_password
from home.views import change_password, index
from shop.views import _cart_id
from django.core.mail import send_mail
from .utils import send_otp, send_otp_2
import pyotp
import requests


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
            password =form.cleaned_data.get('password1')
            
            send_otp(request)
            request.session['encrypted_password'] = make_password(password)
            return redirect(otp_view)
    context = {'form' : form}
    return render(request, 'user_auth/user_signup.html', context)

def log_in(request):
    if request.POST:
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            if user.is_block: 
                messages.error(request, 'Your account is blocked. Please contact support.')
                return redirect('log_in')
            elif not user.is_block: 
                try:
                    cart = Cart.objects.get(cart_id=_cart_id(request))
                    is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                    if is_cart_item_exists:
                        cart_items = CartItem.objects.filter(cart=cart)

                        product_variation=[]
                        for item in cart_items:
                            variation = item.variations.all()
                            product_variation.append(list(variation))
                    
                        cart_item = CartItem.objects.filter(user=user)

                        ex_var_list=[]
                        id=[]
                        for item in cart_item:
                            existing_variation = item.variations.all()
                            ex_var_list.append(list(existing_variation))
                            id.append(item.id)

                        for pr in product_variation:
                            if pr in ex_var_list:
                                index = ex_var_list.index(pr)
                                item_id = id[index]
                                item = CartItem.objects.get(id=item_id)
                                item.quantity += 1
                                item.user = user
                                item.save()
                            else:
                                cart_item = CartItem.objects.filter(cart=cart)
                                for item in cart_items:
                                    item.user = user
                                    item.save()
             
                    if cart.coupon:
                        user.coupon=cart.coupon
                        user.save()
                        
                except:
                    pass
                login(request, user)
                url = request.META.get('HTTP_REFERER')
                try:
                    query = requests.utils.urlparse(url).query
                    params= dict(x.split('=') for x in query.split('&'))
                    if 'next' in params:
                        next_page = params['next']
                        return redirect(next_page)
                except:
                    return redirect('home')
            else:
                messages.error(request, 'Invalid username or password')
                return redirect('log_in')
        else:
            messages.error(request, 'Invalid username or password')
            return redirect('log_in')
        

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
                    encrypted_password = request.session['encrypted_password']
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
                    del request.session['otp_valid_date']
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
    messages.info(request, 'The OTP has sent again, please check now.')
    return redirect(otp_view)


def forgot_password(request):
    if request.POST:     
        email = request.POST['email']
        request.session['email']=email
        is_user_exists = User.objects.all().filter(email=email).exists()
        if is_user_exists:
            send_otp_2(request)
            return redirect(forgot_password_otp)
        else:
            messages.error(request, 'User not found')
    return render(request, 'user_auth/forgot_password.html')
            

def forgot_password_otp(request):
    if request.POST:
        otp = request.POST['otp']

        otp_secret_key = request.session['otp_secret_key']
        otp_valid_date = request.session['otp_valid_date']

        if otp_secret_key and otp_valid_date is not None:
            valid_until = datetime.fromisoformat(otp_valid_date)
            if valid_until > datetime.now():
                totp = pyotp.TOTP(otp_secret_key, interval=60)
                if totp.verify(otp):
                    messages.success(request, 'The OTP has verified successfully.')
                    del request.session['otp_secret_key']
                    del request.session['otp_valid_date']
                    return redirect(update_password)
                else:
                    messages.error(request, 'Incorrect OTP. Please double-check and try again.')
            else:
                messages.error(request, 'OTP has expired. Please request a new OTP.')
        else:
            messages.error(request, 'An unexpected error occurred during OTP verification. Please try again later.')
    return render(request, 'user_auth/forgot_password_otp.html')


def resend_otp_2(request):
    send_otp_2(request)
    messages.info(request, 'The OTP has sent again, please check now.')
    return redirect(forgot_password_otp)


def update_password(request):
    if request.POST:
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        if password1 == password2:
            user = User.objects.get(email__exact=request.session['email'])
            user.set_password(password1)
            user.save()
            messages.success(request, 'The password has upated')
            return redirect(log_in)
        else:
            messages.error(request, 'The password did not match')
    return render(request, 'user_auth/update_password.html')
def log_out(request):
    logout(request)
    return redirect(index)