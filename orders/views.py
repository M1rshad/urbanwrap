from codecs import oem_decode
from django.shortcuts import get_object_or_404, render, redirect, HttpResponse
from shop.models import CartItem
from home.models import Product
from user_auth.models import ShippingAddress
from .models import Order, OrderProduct,Payment, Wallet, WalletTransaction
from .forms import OrderForm
import datetime
from django.urls import reverse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from paypal.standard.forms import PayPalPaymentsForm
import uuid
from django.core.mail import send_mail
from django.contrib import messages
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
    if current_user.coupon and grand_total >= current_user.coupon.minimum_amount:
        grand_total -= request.user.coupon.discounted_price
    shipping_address=None
    try:
        shipping_address = get_object_or_404(ShippingAddress,user=request.user, status=True)
    except:
        pass
    if not shipping_address:
        messages.error(request, 'Please select an address before checking out')
        return redirect('checkout')
    if request.POST:
        form = OrderForm(request.POST)
        if form.is_valid() and shipping_address:
            data=Order()
            data.user = current_user
            data.first_name = shipping_address.first_name
            data.last_name = shipping_address.last_name
            data.email = shipping_address.email
            data.phone = shipping_address.phone
            data.address_line_1 = shipping_address.address_line_1
            data.address_line_2 = shipping_address.address_line_2
            data.country = shipping_address.country
            data.state = shipping_address.state
            data.city = shipping_address.city
            data.pin_code = shipping_address.pin_code
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
    current_user = request.user

    order = get_object_or_404(Order,id=order_id, user=current_user, is_ordered=False)
    order.status = 'Accepted'
    order.is_ordered = True
    order.save()

    payment_id = uuid.uuid4().hex
    payment = Payment.objects.create(
        user=current_user,
        payment_id=payment_id,
        payment_method='Cash On Delivery',
        amount_paid=order.order_total,
        status='Pending'
    )

    order.payment = payment
    order.save()


    #order confirmation email
    subject = 'Order confirmation'
    message = f"""
    Hi {request.user.username},
    Your order has been received!
    Order Number = {order.order_number} 
    """
    send_mail(subject, message, "abdullamirshadcl@gmail.com", [request.user.email,], fail_silently=False)


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

        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variation.set(product_variation)
        orderproduct.save()

        #Reduce the stock
        product = Product.objects.get(id=item.product_id)
        product_variations = product.variant.all()
        quantity = orderproduct.quantity
        for variation in product_variations:
            for i in product_variation:
                if i==variation:
                    variation.stock -= quantity
                    variation.save()

    #clear cart after placing order
    CartItem.objects.filter(user=request.user).delete()

    #clear the coupon
    current_user.coupon = None
    current_user.save()

    order = Order.objects.get(id=order_id, user=current_user)
    order_subtotal = order.order_total - order.tax
    context={
        'order':order,
        'order_subtotal':order_subtotal
    }
    return render(request, 'orders/order_completed.html', context)


def wallet_completed(request, order_id):
    current_user = request.user

    order = get_object_or_404(Order,id=order_id, user=current_user, is_ordered=False)
    order.status = 'Accepted'
    order.is_ordered = True
    order.save()

    payment_id = uuid.uuid4().hex
    payment = Payment.objects.create(
        user=current_user,
        payment_id=payment_id,
        payment_method='Wallet',
        amount_paid=order.order_total,
        status='Completed'
    )
    order.payment = payment
    order.save()

    wallet = Wallet.objects.get(user=current_user)
    wallet.balance -= order.order_total
    wallet.save()

    wallet_transaction = WalletTransaction.objects.create(
            transaction_id=str(uuid.uuid4().int)[:12],
            wallet=wallet,
            amount=order.order_total,
            transaction_type='debit',
            order_reference=order,
            updated_balance=wallet.balance,

        )

    #order confirmation email
    subject = 'Order confirmation'
    message = f"""
    Hi {request.user.username},
    Your order has been received!
    Order Number = {order.order_number} 
    """
    send_mail(subject, message, "abdullamirshadcl@gmail.com", [request.user.email,], fail_silently=False)


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

        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variation.set(product_variation)
        orderproduct.save()

        #Reduce the stock
        product = Product.objects.get(id=item.product_id)
        product_variations = product.variant.all()
        quantity = orderproduct.quantity
        for variation in product_variations:
            for i in product_variation:
                if i==variation:
                    variation.stock -= quantity
                    variation.save()

    #clear cart after placing order
    CartItem.objects.filter(user=request.user).delete()

    #clear the coupon
    current_user.coupon = None
    current_user.save()


    order = Order.objects.get(id=order_id, user=current_user)
    order_subtotal = order.order_total - order.tax
    context={
        'order':order,
        'order_subtotal':order_subtotal
    }
    return render(request, 'orders/order_completed.html', context)


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
    
    #order confirmation email
    subject = 'Order confirmation'
    message = f"""
    Hi {request.user.username},
    Your order has been received!
    Order Number = {order.order_number} 
    """
    send_mail(subject, message, "abdullamirshadcl@gmail.com", [request.user.email,], fail_silently=False)

    
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

        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variation.set(product_variation)
        orderproduct.save()

        #Reduce the stock
        product = Product.objects.get(id=item.product_id)
        product_variations = product.variant.all()
        quantity = orderproduct.quantity
        for variation in product_variations:
            for i in product_variation:
                if i==variation:
                    variation.stock -= quantity
                    variation.save()

    #clear cart after placing order
    CartItem.objects.filter(user=request.user).delete()
    
    #clear the coupon
    current_user.coupon = None
    current_user.save

    order = Order.objects.get(id=order_id, user=current_user)
    order_subtotal = order.order_total - order.tax
    context={
        'order':order,
        'order_subtotal':order_subtotal
    }

    return render(request, 'orders/payment_completed.html', context)


def paypal_payment_failed(request):
    return render(request, 'orders/payment_failed.html')



