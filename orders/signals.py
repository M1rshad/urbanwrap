from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received
from django.dispatch import receiver



@receiver(valid_ipn_received)
def paypal_payment_received(sender, **kwargs):
    print('Signal received')
    ipn_obj = sender
    print('IPN Object:', ipn_obj)

    if ipn_obj.payment_status == ST_PP_COMPLETED:
        print('Payment completed')
        order_number = ipn_obj.item_name
        print('Order number:', order_number)
            
            # ... rest of your code ...

#     print('signal recieved')
#     ipn_obj = sender
#     if ipn_obj.payment_status == ST_PP_COMPLETED:
#         print('payment completed')
#         order_number = ipn_obj.item_name
#         print(order_number)
#         order = Order.objects.get(order_number=order_number)
#         order.is_ordered =True
#         order.save()