from django.shortcuts import render
from .models import Product
# Create your views here.
def index(request):
    featured = Product.objects.all().order_by('-priority','id')[:4] 
    context = {
        'featured':featured,
    }
    return render(request, 'home/index.html', context)

def dashboard(request):
    return render(request, 'home/dashboard.html')