from django.shortcuts import render
from home.models import Product

# Create your views here.
def shop(request):
    products = Product.objects.all().filter(is_available=True)
    product_count = products.count()
    context = {
        'products' : products,
        'product_count' : product_count      
        }
    return render(request, 'shop/shop.html', context)


def product_detail(request, product_slug):
    try:
        single_product = Product.objects.get(slug=product_slug)
    except Exception as e:
        raise e
    context = {
        'single_product' : single_product,
        }
    return render(request, 'shop/product_detail.html', context)