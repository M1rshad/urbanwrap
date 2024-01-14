from django.contrib import admin
from .models import Category,Product,Variation
# Register your models here.


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug' : ('category_name',)}

admin.site.register(Category, CategoryAdmin)
admin.site.register(Product)
admin.site.register(Variation)
