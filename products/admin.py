from django.contrib import admin
from .models import Product, UserTG, Promocode, UserCart, UsedPromocode


# Register your models here.





@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    search_fields = ['product_name', 'id']
    list_filter = ['created_at']
    list_display = ['id', 'product_name', 'created_at']
    ordering = ['-id']


@admin.register(UserCart)
class UserCartAdmin(admin.ModelAdmin):
    pass


@admin.register(Promocode)
class PromocodeAdmin(admin.ModelAdmin):
    search_fields = ['promocode_code', 'id']
    list_filter = ['created_at']
    list_display = ['id', 'promocode_code', 'created_at']
    ordering = ['-id']


@admin.register(UserTG)
class UserTGAdmin(admin.ModelAdmin):
    search_fields = ['user_name', 'id']
    list_filter = ['created_at']
    list_display = ['id', 'user_tg_id', 'user_name', 'created_at']
    ordering = ['-id']


@admin.register(UsedPromocode)
class UsedPromocodeAdmin(admin.ModelAdmin):
    pass