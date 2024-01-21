from django.urls import path
from . import views

urlpatterns = [
    path('shop', views.shop, name='shop'),
    path('shop/<slug:product_slug>', views.product_detail, name='product_detail'),
    path('cart/', views.cart, name='cart'),
    path('add-cart/<int:product_id>/', views.add_cart, name='add_cart'),
    path('remove-cart-item/<int:product_id>/', views.remove_cart_item, name='remove_cart_item'),
    path('decrement-cart-item/<int:product_id>/', views.decrement_cart, name='decrement_cart'),



]