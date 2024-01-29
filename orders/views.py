from django.shortcuts import render, redirect, HttpResponse
from shop.models import CartItem
from .models import Order
from .forms import OrderForm
import datetime
from django.urls import reverse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from paypal.standard.forms import PayPalPaymentsForm
from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received
from django.dispatch import receiver
import uuid
# Create your views here.



def payments(request):
    return render(request, 'orders/payments.html')


def place_order(request, total=0, quantity=0):
    current_user = request.user
    
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()

    if cart_count <= 0 :
        return redirect('shop')
    
    grand_total = 0
    tax = 0

    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity

    tax =  0.02 * total
    grand_total = total + tax

    if request.POST:
        form = OrderForm(request.POST)
        if form.is_valid():
            data=Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.email = form.cleaned_data['email']
            data.phone = form.cleaned_data['phone']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.pin_code = form.cleaned_data['pin_code']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()

            yr = int(datetime.date.today().strftime("%Y"))
            dt = int(datetime.date.today().strftime("%d"))
            mt = int(datetime.date.today().strftime("%m"))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d")
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            host = request.get_host()
            paypal_dict ={
                'business':settings.PAYPAL_RECEIVER_EMAIL,
                'amount': grand_total,
                'item_name': order_number,
                'invoice' : uuid.uuid4(),
                'currency_code': 'USD',
                'notify_url' : 'http://{}{}'.format(host, reverse('paypal-ipn')),
                'return_url' : 'http://{}{}'.format(host, reverse('payment_completed')),
                'cancel_url' : 'http://{}{}'.format(host, reverse('payment_failed'))
            }
            paypal_payment_button = PayPalPaymentsForm(initial=paypal_dict)
            context= {
                'order':order, 
                'cart_items':cart_items,
                'total':total, 
                'tax':tax,
                'grand_total':grand_total,
                'paypal_payment_button':paypal_payment_button,
            }
            return render(request, 'orders/payments.html', context)
        else:
            return redirect('checkout')
        

def payment_completed(request):
    return render(request, 'orders/payment_completed.html')


def payment_failed(request):
    return render(request, 'orders/payment_failed.html')

@receiver(valid_ipn_received)
def paypal_payment_received(sender, **kwargs):
    try:
        print('Signal received')
        ipn_obj = sender
        print('IPN Object:', ipn_obj)

        if ipn_obj.payment_status == ST_PP_COMPLETED:
            print('Payment completed')
            order_number = ipn_obj.item_name
            print('Order number:', order_number)
            
            # ... rest of your code ...

    except Exception as e:
        print('Error processing IPN:', str(e))
#     print('signal recieved')
#     ipn_obj = sender
#     if ipn_obj.payment_status == ST_PP_COMPLETED:
#         print('payment completed')
#         order_number = ipn_obj.item_name
#         print(order_number)
#         order = Order.objects.get(order_number=order_number)
#         order.is_ordered =True
#         order.save()

