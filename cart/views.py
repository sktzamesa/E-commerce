# cart/views.py
from django.shortcuts import render, redirect,get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from products.models import Product
from .models import Order, OrderItem
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from decimal import Decimal
from django.contrib import messages
import json
@require_POST
def cart_add(request, product_id):
    cart = request.session.get('cart', {})
    product = get_object_or_404(Product, pk=product_id)

    if str(product_id) in cart:
        if 'quantity' in cart[str(product_id)]:
            cart[str(product_id)]['quantity'] += 1
        else:
            cart[str(product_id)]['quantity'] = 1
    else:

        cart[str(product_id)] = {
            'quantity': 1,
            'price': str(product.price)
        }

    request.session['cart'] = cart

    return redirect('cart_view')
@login_required
@require_POST
def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})

    # If the item isn't in the cart, return a 400 JSON error
    if str(product_id) not in cart:
        return JsonResponse({'error': 'Product not in cart'}, status=400)

    # Remove it and save
    del cart[str(product_id)]
    request.session['cart'] = cart

    # Recalculate the total
    total_price = Decimal('0.00')
    for item in cart.values():
        total_price += Decimal(str(item['price'])) * item['quantity']

    # Return the updated cart state
    return JsonResponse({
        'cart': cart,
        'total_price': str(total_price),
    })

# View cart details
def cart_view(request):
    cart_items = request.session.get('cart', {})
    cart_details = []
    total_price = Decimal('0.00')

    for product_id, item in cart_items.items():
        product = get_object_or_404(Product, pk=product_id)
        item_price = Decimal(str(item['price']))
        quantity = int(item['quantity'])

        item_details = {
            'product_id': product.id,
            'name': product.name,
            'image_url': product.image.url if product.image else '/static/images/default_image.jpg',
            'description': product.description,
            'price': item_price,
            'quantity': quantity,
            'total_price': item_price * quantity
        }

        cart_details.append(item_details)
        total_price += item_details['total_price']

    return render(request, 'cart/cart_view.html', {
        'cart_items': cart_details,
        'total_price': total_price
    })


@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect('cart_view')

    total_price = sum(Decimal(item['price']) * item['quantity'] for item in cart.values())

    if request.method == 'POST':
        # Create order
        order = Order.objects.create(user=request.user, total_price=total_price)

        # Create order items
        for product_id, item in cart.items():
            product = get_object_or_404(Product, id=product_id)
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item['quantity'],
                price=item['price']
            )
        request.session['cart'] = {}
        return redirect('order_confirmation', order_id=order.id)

    return render(request, 'cart/checkout.html', {'total_price': total_price})

@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'cart/order_confirmation.html', {'order': order})



@login_required
@require_POST
def update_cart(request, product_id):
    # load or initialize cart
    cart = request.session.get('cart', {})

    # ensure item exists
    if str(product_id) not in cart:
        return JsonResponse({'error': 'Product not found in cart'}, status=400)

    # parse incoming JSON
    try:
        payload = json.loads(request.body)
        quantity = int(payload.get('quantity', 1))
        if quantity < 1:
            raise ValueError("Quantity must be >= 1")
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        return JsonResponse({'error': 'Invalid quantity'}, status=400)

    # sanity check product exists
    get_object_or_404(Product, pk=product_id)

    # update session cart
    cart[str(product_id)]['quantity'] = quantity
    request.session['cart'] = cart

    # recalculate total
    total_price = Decimal('0.00')
    for item in cart.values():
        total_price += Decimal(str(item['price'])) * item['quantity']

    # build JSON response
    return JsonResponse({
        'cart': cart,
        'total_price': str(total_price),
    })