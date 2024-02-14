from django.urls import path
from . import views

urlpatterns = [
    path('place-order/', views.place_order, name='place_order'),
    path('payments/', views.payments, name='payments'),
    path('payment-completed/<int:order_id>', views.paypal_payment_completed, name='payment_completed'),
    path('payment-failed/<int:order_id>', views.paypal_payment_failed, name='payment_failed'),
    path('order-completed/<int:order_id>', views.cod_completed, name='cod_completed'),
    path('wallet-order-completed/<int:order_id>', views.wallet_completed, name='wallet_completed')


]
