from .models import Cart, CartItem, Wishlist, WishlistItem
from home.models import Category, Variation
from .views import _cart_id, _wishlist_id

def counter(request):
    item_count = 0
    if 'admin' in request.path:
        return {}
    else:
        try:
            cart = Cart.objects.filter(cart_id = _cart_id(request))
            if request.user.is_authenticated:
                cart_items = CartItem.objects.all().filter(user=request.user)
            else:
                cart_items = CartItem.objects.all().filter(cart=cart[:1])
            for cart_item in cart_items:
                item_count += cart_item.quantity
        except Cart.DoesNotExist:
            item_count = 0
    return dict(item_count=item_count)


def wishlist_counter(request):
    wishlist_item_count = 0
    if 'admin' in request.path:
        return {}
    else:
        try:
            wishlist = Wishlist.objects.filter(wishlist_id = _wishlist_id(request))
            if request.user.is_authenticated:
                wishlist_items = WishlistItem.objects.all().filter(user=request.user)
            else:
                wishlist_items = WishlistItem.objects.all().filter(wishlist=wishlist[:1])
            wishlist_item_count = wishlist_items.count()
        except Wishlist.DoesNotExist:
            wishlist_item_count = 0
    return dict(wishlist_item_count=wishlist_item_count)
            

def category_filter(request):
    cat_filter = Category.objects.all()
    return dict(cat_filter=cat_filter)
