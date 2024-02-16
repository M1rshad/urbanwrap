from django.db import models
from PIL import Image
# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser
from home.models import Product
import uuid

# Create your models here.

class User(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    is_block = models.BooleanField(default=False)

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
    user = models.OneToOneField(User, on_delete=models.CASCADE)
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
                      
    
class ShippingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    first_name = models.CharField(max_length=50) 
    last_name = models.CharField(max_length=50) 
    phone = models.CharField(max_length=15) 
    email = models.EmailField(max_length=50) 
    address_line_1 = models.CharField(max_length=50) 
    address_line_2 = models.CharField(max_length=50)
    country = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    pin_code = models.CharField(max_length=10, null=True, blank=True)
    status = models.BooleanField(default=True)


    def save(self, *args, **kwargs):
        if self.status:
            ShippingAddress.objects.filter(user=self.user, status=True).update(status=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.first_name

