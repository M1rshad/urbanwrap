from email import message
from email.headerregistry import Address
from django.shortcuts import get_object_or_404, redirect, render
from .models import Product, Category
from user_auth.models import ShippingAddress, User, UserProfile
from admin_panel.forms import EditUserForm
from user_auth.forms import UserProfileForm, ShippingAddressForm
from orders.models import Order,Wallet, WalletTransaction
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
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


@login_required(login_url='log_in')
def my_orders(request):
    orders = Order.objects.all().filter(user=request.user, is_ordered=True).order_by('-id')
    context={
        'orders':orders,
    }
    return render(request, 'home/my_orders.html', context)

@login_required(login_url='log_in')
def cancel_orders(request, order_id):
    order_obj = Order.objects.get(id=order_id)
    order_obj.status = 'Cancelled'
    order_obj.save()
    if order_obj.payment.status == 'Completed':
        wallet = Wallet.objects.get(user=request.user)
        wallet.balance += order_obj.order_total
        wallet.save()
        wallet_transaction = WalletTransaction.objects.create(
            transaction_id=str(uuid.uuid4().int)[:12],
            wallet=wallet,
            amount=order_obj.order_total,
            transaction_type='credit',
            order_reference=order_obj,
            updated_balance=wallet.balance,
        )
    
    order_items = order_obj.orderproduct_set.all()
    for item in order_items:
        product_variation = item.variation.all()

        #update the stock
        product = Product.objects.get(id=item.product_id)
        product_variations = product.variant.all()
        quantity = item.quantity
        for variation in product_variations:
            for i in product_variation:
                if i==variation:
                    variation.stock += quantity
                    variation.save()


    #order confirmation email
    subject = 'Order cancellation'
    message = f"""
    Hi {request.user.username},
    Your order has been cancelled!
    Order Number = {order_obj.order_number} 
    """
    send_mail(subject, message, "abdullamirshadcl@gmail.com", [request.user.email,], fail_silently=False)
    
    return redirect('my_orders')


@login_required(login_url='log_in')
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


@login_required(login_url='log_in')
def my_address(request):
    addresses = ShippingAddress.objects.filter(user=request.user)
    context={
        'addresses':addresses,
    }
    return render(request, 'home/my_address.html',context)

@login_required(login_url='log_in')
def add_address(request):
    
    max_address_allowed=3
    existing_address_count = ShippingAddress.objects.filter(user=request.user).count()

    if existing_address_count >= max_address_allowed:
        messages.error(request, 'Address limit exceeded')
        return redirect('my_address')
    
    form = ShippingAddressForm()
    if request.POST:
        form = ShippingAddressForm(request.POST)
        if form.is_valid():
            address= form.save(commit=False)
            address.user=request.user
            address.save()
            return redirect('my_address')
    else:
        form = ShippingAddressForm()
    context ={'form':form}
    return render(request, 'home/add_address.html', context)


@login_required(login_url='log_in')
def edit_address(request, address_id):
    address = ShippingAddress.objects.get(id=address_id)
    if request.POST:
        form = ShippingAddressForm(request.POST, instance=address)
        if form.is_valid():
            address= form.save(commit=False)
            address.user=request.user
            address.save()
            return redirect('my_address')
    else:
        form = ShippingAddressForm(instance=address)
    context ={'form':form}
    return render(request, 'home/edit_address.html', context)


@login_required(login_url='log_in')
def delete_address(request, address_id):
    address = ShippingAddress.objects.get(id=address_id)
    address.delete()
    return redirect('my_address')


@login_required(login_url='log_in')
def select_address(request, address_id):
    shipping_address = ShippingAddress.objects.get(id=address_id)
    shipping_address.status=True
    shipping_address.save()
    return redirect('my_address')


@login_required(login_url='log_in')
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


@login_required(login_url='log_in')
def wallet(request):
    wallet = Wallet.objects.get(user=request.user)
    transaction_history = WalletTransaction.objects.filter(wallet=wallet).order_by('-id')
    context = {
        'wallet': wallet,
        'transaction_history':transaction_history,
    }
    return render(request, 'home/wallet.html', context)