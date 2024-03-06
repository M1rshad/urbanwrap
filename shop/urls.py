from django.urls import path
from . import views

urlpatterns = [
    path('shop/', views.shop, name='shop'),
    path('shop/category/<slug:category_slug>', views.shop, name='products_by_category'),
    path('shop/category/<slug:category_slug>/<slug:product_slug>', views.product_detail, name='product_detail'),
    path('check_stock/', views.check_stock, name='check_stock'),
    path('cart/', views.cart, name='cart'),
    path('add-cart/<int:product_id>/', views.add_cart, name='add_cart'),
    path('remove-cart-item/<int:product_id>/<int:cart_item_id>', views.remove_cart_item, name='remove_cart_item'),
    path('decrement-cart-item/<int:product_id>/<int:cart_item_id>', views.decrement_cart, name='decrement_cart'),
    #path('check_stock_cart/', views.check_stock_cart, name='check_stock_cart'),
    path('shop/search/', views.search, name='search'),
    path('cart/checkout/', views.checkout, name='checkout'),
    path('cart/checkout/select-address/<int:address_id>', views.select_address_checkout, name='select_address_checkout'),
    path('cart/checkout/delete-address/<int:address_id>', views.delete_address_checkout, name='delete_address_checkout'),
    path('cart/checkout/edit-address/<int:address_id>', views.edit_address_checkout, name='edit_address_checkout'),
    path('cart/checkout/add-address/', views.add_address_checkout, name='add_address_checkout'),
    path('cart/remove-coupon/<cart_id>', views.remove_coupon, name='remove_coupon'),
    path('cart/remove-coupons/', views.remove_coupons, name='remove_coupons'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/get_stock_status/', views.get_stock_status, name='get_stock_status'),
    path('add-wishlist/<int:product_id>/', views.add_wishlist, name='add_wishlist'),
    path('remove-wishlist-item/<int:product_id>/<int:wishlist_item_id>', views.remove_wishlist_item, name='remove_wishlist_item'),


]