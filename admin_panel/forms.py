from django import forms 
from user_auth.models import User, Coupon
from home.models import Category, Product, Variation, ProductImages
from orders.models import Order, Offer
from django.core.validators import FileExtensionValidator


class EditUserForm(forms.ModelForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name')



class AddCategoryForm(forms.ModelForm):
    cat_image = forms.ImageField(validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp'])], required=False)
    class Meta:
        model = Category
        fields = ('category_name', 'slug', 'description', 'cat_image')




class AddProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = ('product_name', 'slug', 'description', 'price', 'is_available', 'category')


class AddVariantForm(forms.ModelForm):

    class Meta:
        model = Variation
        fields = ('product', 'variation_category', 'variation_value', 'is_active')


class ProductImageForm(forms.ModelForm):
    image = forms.ImageField(validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp'])], )
    delete_image = forms.BooleanField(required=False, initial=False, widget=forms.CheckboxInput(attrs={'class': 'delete-checkbox'}))
    class Meta:
        model = ProductImages
        fields =('image','delete_image')

   
class AddCouponForm(forms.ModelForm):

    class Meta:
        model = Coupon
        fields = ('coupon_code', 'discounted_price', 'minimum_amount', 'is_expired')


class UpdateOrderForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = ('status',)


class AddOfferForm(forms.ModelForm):

    class Meta:
        model = Offer
        fields = ('offer_name', 'discount_percentage', 'valid_to', 'products')