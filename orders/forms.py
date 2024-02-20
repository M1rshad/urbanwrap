from django import forms
from .models import Order, Payment


class OrderForm(forms.ModelForm):
    class Meta: 
        model = Order
        fields = ['order_note', 'payment_method']


class OrderUpdateForm(forms.ModelForm):
    class Meta: 
        model = Order
        fields = ['status',]


class PaymentUpdateForm(forms.ModelForm):
    class Meta: 
        model = Payment
        fields = ['status',]

