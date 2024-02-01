from django.shortcuts import render
from .models import Product, Category
# Create your views here.
def index(request):
    featured = Product.objects.all().filter(is_active=True).order_by('-priority','id')[:4] 
    t_shirt_category = Category.objects.get(category_name='T shirt')
    recent_t_shirts = Product.objects.all().filter(category=t_shirt_category, is_active=True).order_by('-created_date')[:4]
    joggers_category = Category.objects.get(category_name='Joggers')
    recent_joggers = Product.objects.all().filter(category=joggers_category, is_active=True).order_by('-created_date')[:4]
    sweatshirts_category = Category.objects.get(category_name='Sweatshirts')
    recent_sweatshirts = Product.objects.all().filter(category=sweatshirts_category, is_active=True).order_by('-created_date')[:4]
    trousers_category = Category.objects.get(category_name='Trousers')
    recent_trousers = Product.objects.all().filter(category=trousers_category, is_active=True).order_by('-created_date')[:4]
    context = {
        'featured':featured,
        'recent_t_shirts':recent_t_shirts,
        'recent_joggers':recent_joggers,
        'recent_sweatshirts':recent_sweatshirts,
        'recent_trousers':recent_trousers
    }
    return render(request, 'home/index.html', context)

def dashboard(request):
    return render(request, 'home/dashboard.html')