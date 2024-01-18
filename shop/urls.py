from django.urls import path
from . import views

urlpatterns = [
    path('shop', views.shop, name='shop'),
    path('shop/<slug:product_slug>', views.product_detail, name='product_detail'),
    path('cart', views.cart, name='cart'),

]