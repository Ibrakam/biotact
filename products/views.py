from django.shortcuts import render, redirect
from .models import Product, UserCart


def product_list(request):
    products = Product.objects.all()
    return render(request, 'all_products.html', {'products': products})


def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    user_id = request.user.id if request.user.is_authenticated else None
    cart, created = UserCart.objects.get_or_create(user_id=user_id, products=product,
                                                   defaults={'quantity': 1, 'total_price': product.price})

    if not created:
        cart.quantity += 1
        cart.total_price += product.price
        cart.save()

    return redirect('all_products')


def confirm_order(request):
    user_id = request.user.id if request.user.is_authenticated else None
    cart_items = UserCart.objects.filter(user_id=user_id)

    return redirect('/')
