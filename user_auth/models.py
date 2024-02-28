from django.db import models
from PIL import Image
# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser
from home.models import Product
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _

import uuid

# Create your models here.
class Coupon(models.Model):

    coupon_code = models.CharField(max_length=10)
    is_expired = models.BooleanField(default=False)
    discounted_price = models.PositiveIntegerField(default=10, validators=[MinValueValidator(1)])
    minimum_amount = models.PositiveIntegerField(default=100, validators=[MinValueValidator(1)])
    is_active = models.BooleanField(default=True)


    def __str__(self):
        return self.coupon_code

class User(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    is_block = models.BooleanField(default=False)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


    def save(self, *args, **kwargs):
        created = not self.pk 
        super().save(*args, **kwargs)

        if created:
            UserProfile.objects.create(user=self)
            from orders.models import Wallet
            Wallet.objects.create(user=self, card_id=self.generate_card_id(), balance=0)

    def generate_card_id(self):
        # Generate a random 12-digit card ID using uuid
        card_id = str(uuid.uuid4().int)[:12]
        return card_id
    

    def __str__(self):
        return self.username
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile')
    dp = models.ImageField(upload_to='images/dp/', blank=True, null=True)
    bio = models.CharField(max_length=200, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        super(UserProfile, self).save(*args, **kwargs)

        if self.dp:
            img = Image.open(self.dp.path)
            if img.width > 150 or img.height > 150:
                output_size = (150, 150)
                img.thumbnail(output_size)
                img.save(self.dp.path)
                      
    

def validate_phone_number(value):
    if not value.isdigit():
        raise ValidationError(_("Phone number must contain only digits"))
    if len(value) < 10 or len(value) > 15:
        raise ValidationError(_("Phone number must be between 10 and 15 digits"))

def validate_pin_code(value):
    if not value.isdigit():
        raise ValidationError(_("PIN code must contain only digits"))
    if len(value) != 6:  
        raise ValidationError(_("PIN code must be exactly 6 digits"))
    

class ShippingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    first_name = models.CharField(max_length=50) 
    last_name = models.CharField(max_length=50) 
    phone = models.CharField(max_length=15, validators=[validate_phone_number]) 
    email = models.EmailField(max_length=50) 
    address_line_1 = models.CharField(max_length=50) 
    address_line_2 = models.CharField(max_length=50)
    country = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    pin_code = models.CharField(max_length=10, null=True, blank=True, validators=[validate_pin_code])
    status = models.BooleanField(default=True)


    def save(self, *args, **kwargs):
        if self.pk:  # Check if the instance is an existing record
            original_instance = ShippingAddress.objects.get(pk=self.pk)
            if self.status != original_instance.status and self.status:  # Check if status is being changed to True
                ShippingAddress.objects.filter(user=self.user, status=True).exclude(pk=self.pk).update(status=False)
        else:  # New record
            if self.status:
                ShippingAddress.objects.filter(user=self.user, status=True).update(status=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.first_name

