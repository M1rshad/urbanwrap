from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received
from django.dispatch import receiver
import logging

logger = logging.getLogger(__name__)


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
    except Exception as e:
        logger.error(f"Error processing PayPal IPN: {e}")