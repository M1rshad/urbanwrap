from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from home.models import Product, Category, Variation
from orders.models import Coupon
from .models import Cart, CartItem, Wishlist, WishlistItem
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q 
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import ProductFilterForm
# Create your views here.
def shop(request, category_slug=None):
    categories = None
    products = None
    form = None
    
    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug, is_active=True)
        products = Product.objects.filter(category=categories, is_available=True, is_active=True)
        paginator = Paginator(products, 12)
        page = request.GET.get('page')
        paged_product = paginator.get_page(page)
        product_count = products.count()
    else:
        products = Product.objects.all().filter(is_available=True, is_active=True).order_by('id')
        form = ProductFilterForm(request.GET)
        if form.is_valid():
            category = form.cleaned_data.get('category')
            size = form.cleaned_data.get('size')
            min_price = form.cleaned_data.get('min_price')
            max_price = form.cleaned_data.get('max_price')
            if category:
                products = products.filter(category__category_name=category,is_available=True, is_active=True).order_by('id')
            if size:
                products = products.filter(variant__variation_value=size,is_available=True, is_active=True).order_by('id')
            if min_price:
                products = products.filter(price__gte=min_price,is_available=True, is_active=True).order_by('id')
            if max_price:
                products = products.filter(price__lte=max_price,is_available=True, is_active=True).order_by('id')

        paginator = Paginator(products, 12)
        page = request.GET.get('page')
        paged_product = paginator.get_page(page)
        product_count = products.count()
    context = {
        'products' : paged_product,
        'product_count' : product_count,
        'form': form,
        }
    return render(request, 'shop/shop.html', context)


def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        variation = single_product.variant.all().order_by('id')
        in_cart =  CartItem.objects.filter(cart__cart_id=_cart_id(request), product = single_product).exists()
    except Exception as e:
        raise e
    context = {
        'single_product' : single_product,
        'in_cart' : in_cart,
        'variation':variation
        }
    return render(request, 'shop/product_detail.html', context)

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def add_cart(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id) 

    #if user is authenticated
    if current_user.is_authenticated:
        product_variation = []
        if request.POST:
            for item in request.POST:
                key = item
                value = request.POST[key]
        
        try:
            variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
            product_variation.append(variation)
        except:
            pass


        is_cart_item_exists = CartItem.objects.filter(product=product, user=current_user).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, user=current_user)

            ex_var_list=[]
            id=[]
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)

                
            if product_variation in ex_var_list:
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
               
               
                item.save()
            else:
                item = CartItem.objects.create(product=product, quantity=1, user=current_user)  
                if len(product_variation)>0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()
        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                user = current_user
            )
            if len(product_variation)>0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
        return redirect('cart')

    else:
        product_variation = []
        if request.POST:
            for item in request.POST:
                key = item
                value = request.POST[key]
        
        try:
            variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
            product_variation.append(variation)
        except:
            pass

        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id = _cart_id(request)
            )
            cart.save()

        is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, cart=cart)

            ex_var_list=[]
            id=[]
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)

                
            if product_variation in ex_var_list:
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity +=1
                item.save()
            else:
                item = CartItem.objects.create(product=product, quantity=1, cart=cart)  
                if len(product_variation)>0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()
        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                cart = cart
            )
            if len(product_variation)>0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
        return redirect('cart')


def decrement_cart(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product,user=request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request)) 
            cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        if cart_item.quantity > 1 :
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')

def remove_cart_item(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(user=request.user, product=product, id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(cart=cart, product=product, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')


def cart(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0 
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True).order_by('id')
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True).order_by('id')
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax =  0.02 * total
        grand_total = total + tax
        if request.POST:
            coupon = request.POST['coupon']
            coupon_obj = Coupon.objects.filter(coupon_code = coupon)
            if not coupon_obj.exists():
                messages.error(request, 'Invalid Coupon.')
                return redirect('cart')
            if cart.coupon:
                messages.error(request, 'Coupon already exists.')
                return redirect('cart')
            
            if grand_total <= coupon_obj[0].minimum_amount:
                messages.error(request, f'Total amount should be above {coupon_obj.minimum_amount}')
                return redirect('cart')
            
            if coupon_obj[0].is_expired:
                messages.error(request, 'Coupon expired.')
                return redirect('cart')

            cart.coupon = coupon_obj[0]
            cart.save()
            messages.success(request, 'Coupon applied.')
            grand_total -= coupon_obj[0].discounted_price

    except Cart.DoesNotExist:
        pass
    

    context = {
        'total':total,
        'quantity':quantity,
        'cart_items' : cart_items,
        'tax' : tax,
        'grand_total':grand_total,
        #'cart':cart,
        
    }
    return render(request, 'shop/cart.html', context)
    

def remove_coupon(request, cart_id):
    cart = Cart.objects.get(cart_id=cart_id)
    cart.coupon = None
    cart.save()
    messages.success(request, 'Coupon removed.')
    return redirect('cart')


def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
            product_count = products.count()
    context = {
        'products':products,
        'product_count':product_count
    }
    return render(request, 'shop/shop.html', context)


@login_required(login_url='log_in')
def checkout(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0 
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True).order_by('id')
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True).order_by('id')
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax =  0.02 * total
        grand_total = total + tax
    except Cart.DoesNotExist:
        pass
    context = {
        'total':total,
        'quantity':quantity,
        'cart_items' : cart_items,
        'tax' : tax,
        'grand_total':grand_total,
    }
    return render(request, 'shop/checkout.html', context)


def _wishlist_id(request):
    wishlist = request.session.session_key
    if not wishlist:
        wishlist = request.session.create()
    return wishlist

def add_wishlist(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id) 

    #if user is authenticated
    if current_user.is_authenticated:

        is_wishlist_item_exists = WishlistItem.objects.filter(product=product, user=current_user).exists()
        if is_wishlist_item_exists:
            wishlist_item = WishlistItem.objects.filter(product=product, user=current_user)

        else:
            wishlist_item = WishlistItem.objects.create(
                product = product,
                user = current_user
            )
        return redirect('wishlist')

    else:

        try:
            wishlist = Wishlist.objects.get(wishlist_id=_wishlist_id(request))
        except Wishlist.DoesNotExist:
            wishlist = Wishlist.objects.create(
                wishlist_id = _wishlist_id(request)
            )
            wishlist.save()

        is_wishlist_item_exists = WishlistItem.objects.filter(product=product, wishlist=wishlist).exists()
        if is_wishlist_item_exists:
            wishlist_item = WishlistItem.objects.filter(product=product, wishlist=wishlist)


        else:
            wishlist_item = WishlistItem.objects.create(
                product = product,
                wishlist = wishlist
            )
        return redirect('wishlist')
    

def wishlist(request, wishlist_items=None):
    try:
        if request.user.is_authenticated:
            wishlist_items = WishlistItem.objects.filter(user=request.user, is_active=True).order_by('id')
        else:
            wishlist = Wishlist.objects.get(wishlist_id=_wishlist_id(request))
            wishlist_items = WishlistItem.objects.filter(wishlist=wishlist, is_active=True).order_by('id')

    except Wishlist.DoesNotExist:
        pass
    

    context = {
        'wishlist_items' : wishlist_items,
        #'cart':cart,
    }
    return render(request, 'shop/wishlist.html', context)

def remove_wishlist_item(request, product_id, wishlist_item_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        wishlist_item = WishlistItem.objects.get(user=request.user, product=product, id=wishlist_item_id)
    else:
        wishlist = Wishlist.objects.get(wishlist_id=_wishlist_id(request))
        wishlist_item = WishlistItem.objects.get(wishlist=wishlist, product=product, id=wishlist_item_id)
    wishlist_item.delete()
    return redirect('wishlist')

