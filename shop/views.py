from django.shortcuts import render
from home.models import Product

# Create your views here.
def shop(request):
    products = Product.objects.all().filter(is_available=True)
    context = {'products' : products}
    return render(request, 'shop/shop.html', context)