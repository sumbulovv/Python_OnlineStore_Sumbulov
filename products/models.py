from django.db import models
from pathlib import Path
import hashlib
import uuid


def product_image_path(instance, filename):
    ext = Path(filename).suffix
    hash_name = hashlib.sha256(f"{uuid.uuid4()}{filename}".encode()).hexdigest()
    return f"products/{hash_name}{ext}"


# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    price = models.DecimalField(max_digits=7, decimal_places=2, verbose_name='Цена')
    image = models.ImageField(upload_to=product_image_path, blank=True, null=True, verbose_name='Изображение')
    category = models.ForeignKey('Category', on_delete=models.PROTECT, verbose_name='Категория')
    
    def __str__(self):
        return self.name


class Category(models.Model):
   name = models.CharField(max_length=255, verbose_name='Название')
   
   def __str__(self):
       return self.name
   

class Stock(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, verbose_name='Товар')
    quantity = models.PositiveIntegerField(default=0, verbose_name='Количество')
    
    def __str__(self):
        return f"{self.product.name} - {self.quantity} in stock"