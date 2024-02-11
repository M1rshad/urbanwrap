from email import message
from django.shortcuts import get_object_or_404, redirect, render
from .models import Product, Category
from user_auth.models import User, UserProfile
from admin_panel.forms import EditUserForm
from user_auth.forms import UserProfileForm
from orders.models import Order,Wallet
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import uuid
# Create your views here.
def index(request):
    featured = Product.objects.all().filter(is_active=True).order_by('-priority','id')[:4] 
    t_shirt_category = Category.objects.get(category_name='T shirt')
    recent_t_shirts = Product.objects.all().filter(category=t_shirt_category, is_active=True).order_by('-created_date')[:4]
    joggers_category = Category.objects.get(category_name='Joggers')
    recent_joggers = Product.objects.all().filter(category=joggers_category, is_active=True).order_by('-created_date')[:4]
    sweatshirts_category = Category.objects.get(category_name='Sweatshirts')
    recent_sweatshirts = Product.objects.all().filter(category=sweatshirts_category, is_active=True).order_by('-created_date')[:4]
    trousers_category = Category.objects.get(category_name='Trousers')
    recent_trousers = Product.objects.all().filter(category=trousers_category, is_active=True).order_by('-created_date')[:4]
    context = {
        'featured':featured,
        'recent_t_shirts':recent_t_shirts,
        'recent_joggers':recent_joggers,
        'recent_sweatshirts':recent_sweatshirts,
        'recent_trousers':recent_trousers
    }
    return render(request, 'home/index.html', context)


@login_required(login_url='log_in')
def dashboard(request):
    orders = Order.objects.all().filter(user=request.user, is_ordered=True).order_by('-id')
    order_count = orders.count()
    user_profile = UserProfile.objects.get(user=request.user)
 
    context={
        'orders':orders,
        'order_count':order_count,
        'user_profile':user_profile,
    }
    return render(request, 'home/dashboard.html', context)

def my_orders(request):
    orders = Order.objects.all().filter(user=request.user, is_ordered=True).order_by('-id')
    context={
        'orders':orders,
    }
    return render(request, 'home/my_orders.html', context)


def update_account_details(request):
    user_profile = UserProfile.objects.get(user=request.user)
    if request.POST:
        user_form = EditUserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'The profile has been updated')
            redirect('dashboard')
    else:
        user_form = EditUserForm(instance=request.user)
        profile_form = UserProfileForm(instance=user_profile)
        
    context={
        'user_form':user_form,
        'profile_form':profile_form,
        'user_profile': user_profile,
    }
    return render(request, 'home/account_details.html', context)


def change_password(request):
    if request.POST:
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = User.objects.get(email__exact=request.user.email)
        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Password has been updated')
            else:
                messages.error(request, 'Passwords does not match')
        else:
            messages.error(request, 'Current password is incorrect! Enter a valid password.')

    return render(request, 'home/change_password.html')


def wallet(request):
    wallet = Wallet.objects.get(user=request.user)
        

    context = {
        'wallet': wallet,
    }
    return render(request, 'home/wallet.html', context)