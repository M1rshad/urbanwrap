from django.contrib import admin
from .models import User, UserProfile, ShippingAddress, Coupon

# Register your models here.
admin.site.register(User)
admin.site.register(UserProfile)
admin.site.register(ShippingAddress)
admin.site.register(Coupon)