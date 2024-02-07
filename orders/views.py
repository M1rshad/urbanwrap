from codecs import oem_decode
from django.shortcuts import get_object_or_404, render, redirect, HttpResponse
from shop.models import CartItem
from home.models import Product
from .models import Order, OrderProduct,Payment
from .forms import OrderForm
import datetime
from django.urls import reverse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from paypal.standard.forms import PayPalPaymentsForm
import uuid
# Create your views here.



def payments(request):
    return render(request, 'orders/payments.html')

@csrf_exempt
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
            data.payment_method= form.cleaned_data['payment_method']
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
            paypal_payment_button=None

            if order.payment_method=='cod':
                pass
            if order.payment_method=='paypal':
                host = request.get_host()
                paypal_dict ={
                    'business':settings.PAYPAL_RECEIVER_EMAIL,
                    'amount': order.order_total,
                    'invoice' : uuid.uuid4(),
                    'currency_code': 'USD',
                    'notify_url' : 'https://{}{}'.format(host, reverse('paypal-ipn')),
                    'return_url' : 'http://{}{}'.format(host, reverse('payment_completed', kwargs={'order_id': order.id})),
                    'cancel_url' : 'http://{}{}'.format(host, reverse('payment_failed', kwargs={'order_id': order.id}))
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
        
def cod_completed(request, order_id):
    return render(request, 'orders/order_completed.html')


def paypal_payment_completed(request, order_id):
    current_user = request.user

    order = get_object_or_404(Order,id=order_id, user=current_user, is_ordered=False)
    order.status = 'Accepted'
    order.is_ordered = True
    order.save()

    payment_id = uuid.uuid4().hex
    payment = Payment.objects.create(
        user=current_user,
        payment_id=payment_id,
        payment_method='PayPal',
        amount_paid=order.order_total,
        status='Completed'
    )

    order.payment = payment
    order.save()

    cart_items = CartItem.objects.filter(user=request.user)
    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product.id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.is_ordered = True
        orderproduct.save()

        cart_item = CartItem.objects.get(id=item.product_id)
        product_variation = cart_item.variations.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variation.set(product_variation)
        orderproduct.save()

        #Reduce the stock
        product = Product.objects.get(id=item.id)
        product_variation = product.variations.all()
        quantity = orderproduct.quantity
        for variation in product_variation:
            variation.stock -= quantity
            variation.save()

    #clear cart after placing order
    CartItem.objects.filter(user=request.user).delete()

    return render(request, 'orders/payment_completed.html')


def paypal_payment_failed(request):
    return render(request, 'orders/payment_failed.html')



