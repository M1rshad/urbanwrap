from django.db import models
from user_auth.models import User
from home.models import Product, Variation
# Create your models here.
class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=100)
    amount_paid = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.payment_id
    

class Order(models.Model):

    STATUS = (
        ('New','New'),
        ('Accepted','Accepted'),
        ('Completed','Completed'),
        ('Cancelled','Cancelled'),
    )

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    order_number = models.CharField(max_length=20) 
    first_name = models.CharField(max_length=50) 
    last_name = models.CharField(max_length=50) 
    phone = models.CharField(max_length=15) 
    email = models.EmailField(max_length=50) 
    address_line_1 = models.CharField(max_length=50) 
    address_line_2 = models.CharField(max_length=50) 
    country = models.CharField(max_length=50) 
    state = models.CharField(max_length=50) 
    city = models.CharField(max_length=50) 
    pin_code = models.IntegerField()
    order_note = models.CharField(max_length=100, blank=True)
    order_total = models.FloatField()
    tax = models.FloatField()
    status = models.CharField(max_length=10, choices=STATUS, default='New')
    payment_method=models.CharField(max_length=15) 
    ip = models.CharField(max_length=20, blank=True)
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)        
    updated_at = models.DateTimeField(auto_now=True)


    def full_name(self):
        return f'{self.first_name} {self.last_name}'
    
    def full_address(self):
        return f'{self.address_line_1} {self.address_line_2}'

    def __str__(self):
        return self.first_name
    

class OrderProduct(models.Model):

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation = models.ManyToManyField(Variation,blank=True)
    quantity = models.IntegerField()
    product_price = models.FloatField() 
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)        
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product.product_name
     

    def get_total(self):
        total = self.product.price * self.quantity
        return total

class Coupon(models.Model):

    coupon_code = models.CharField(max_length=10)
    is_expired = models.BooleanField(default=False)
    discounted_price = models.IntegerField(default=10)
    minimum_amount = models.IntegerField(default=100)
    is_active = models.BooleanField(default=True)


    def __str__(self):
        return self.coupon_code
    


class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    card_id = models.CharField(max_length=12, unique=True)
    balance = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.username}'s Wallet"
    


