from django.db import models


class CategoryProducts(models.Model):
    name = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


# Create your models here.
class Product(models.Model):
    product_name = models.CharField(max_length=50, blank=True)
    price = models.BigIntegerField(blank=True)
    description_ru = models.TextField(blank=True)
    description_uz = models.TextField(blank=True)
    product_image = models.FileField(upload_to="product_images")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product_name

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'


class UserTG(models.Model):
    user_tg_id = models.BigIntegerField(blank=True, null=True)
    user_name = models.CharField(max_length=50, blank=True, null=True)
    phone_number = models.CharField(max_length=50, blank=True, null=True)
    lang = models.CharField(default="ru", null=True, max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user_name

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class UsedPromocode(models.Model):
    user_id = models.BigIntegerField(blank=True, null=True)
    promocode = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.promocode

    class Meta:
        verbose_name = 'Использованный промокод'
        verbose_name_plural = 'Использованные промокоды'

class Promocode(models.Model):
    promocode_code = models.CharField(max_length=50, blank=True, null=True)
    discount = models.BigIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.promocode_code

    class Meta:
        verbose_name = 'Промокод'
        verbose_name_plural = 'Промокоды'


class UserCart(models.Model):
    user_id = models.BigIntegerField(blank=True, null=True)
    quantity = models.IntegerField(blank=True, null=True)
    promocode = models.CharField(max_length=50, blank=True, null=True)
    total_price = models.BigIntegerField(blank=True, null=True)
    products = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return str(self.products) if self.products else "No Product"

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
