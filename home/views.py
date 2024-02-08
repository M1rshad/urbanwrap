from email import message
from django.shortcuts import render
from .models import Product, Category
from user_auth.models import User
from orders.models import Order
from django.contrib.auth.decorators import login_required
from django.contrib import messages
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

    #change password
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


    context={
        'orders':orders,
        'order_count':order_count,
    }
    return render(request, 'home/dashboard.html', context)