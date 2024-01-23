from django.urls import path
from . import views

urlpatterns = [
    path('place-order/', views.place_order, name='place_order'),
    path('payments/', views.payments, name='payments'),
    path('payment-completed/', views.payment_completed, name='payment_completed'),
    path('payment-failed/', views.payment_failed, name='payment_failed'),


]
