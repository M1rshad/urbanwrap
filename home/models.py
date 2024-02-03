from email.policy import default
from django.db import models
from django.urls import reverse
from PIL import Image

# Create your models here.
class Category(models.Model):
    category_name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(max_length=255, blank=True)
    cat_image = models.ImageField(upload_to='images/category', blank=True)
    is_active = models.BooleanField(default=True)

    
    def get_url(self):
        return reverse('products_by_category',args=[self.slug])
    

    def __str__(self) -> str:
        return self.category_name
    

class Product(models.Model):
    product_name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(max_length=255, blank=True)
    price = models.PositiveIntegerField()
    is_available = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    priority =  models.IntegerField(default=0, blank=True)
    category = models.ForeignKey(Category, on_delete = models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)


    def get_url(self):
        return reverse('product_detail',args=[self.category.slug, self.slug])

    def __str__(self) -> str:
        return self.product_name


class ProductImages(models.Model):
    product= models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_img', default=1)
    image=models.ImageField(upload_to='images/products')
    
    def save(self, *args, **kwargs):
        super(ProductImages, self).save(*args, **kwargs)

        if self.image:
            img = Image.open(self.image.path)
            if img.width > 500 or img.height > 500:
                output_size = (500, 500) 
                img.thumbnail(output_size)
                img.save(self.image.path)
    
    


    def __str__(self):
        return f"{self.product.product_name} - Image"


    
variation_category_choices={
    'size': 'size'
}

class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variant')
    variation_category = models.CharField(max_length=100, choices=variation_category_choices)
    variation_value=models.CharField(max_length=100)
    stock = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)

    
    def __str__(self):
        return f"{self.product}-{self.variation_category}- {self.variation_value}"
    