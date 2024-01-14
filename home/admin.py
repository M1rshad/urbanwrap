from django.contrib import admin
from .models import Category,Product,Variation,ProductImages
from admin_panel.forms import ProductImageForm
# Register your models here.


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug' : ('category_name',)}

class ProductImageInline(admin.TabularInline): 
    model = ProductImages
    form = ProductImageForm
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]
    prepopulated_fields = {'slug' : ('product_name',)}

admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Variation)
