from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render
from products.models import Product

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})



def home(request):
    return render(request, 'home.html')


# Product list view
def product_list(request):
    products = Product.objects.all()
    return render(request, 'products/product_list.html', {'products': products})


# Cart view
def cart_view(request):
    cart_items = request.session.get('cart', {})
    cart_details = []
    total_price = 0

    for product_id, item in cart_items.items():
        product = get_object_or_404(Product, pk=product_id)
        item_details = {
            'product_id': product.id,
            'name': product.name,
            'image_url': product.image.url,  # Assuming 'image' is the field name for the product image
            'description': product.description,
            'price': item['price'],
            'quantity': item['quantity'],
            'total_price': item['price'] * item['quantity']
        }
        cart_details.append(item_details)
        total_price += item['price'] * item['quantity']

    return render(request, 'cart/cart_view.html', {
        'cart_items': cart_details,
        'total_price': total_price
    })


# Add to cart view
def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})
    cart_item = cart.get(str(product_id))

    if cart_item:
        cart_item['quantity'] += 1
    else:
        cart_item = {
            'name': product.name,
            'price': float(product.price),
            'quantity': 1
        }

    cart[str(product_id)] = cart_item
    request.session['cart'] = cart
    return redirect('cart_view')


# Login view
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()

    return render(request, 'registration/login.html', {'form': form})


# Logout view
def logout_view(request):
    logout(request)
    return redirect('home')


# Remove from cart view
def cart_remove(request, product_id):
    cart = request.session.get('cart', {})

    if str(product_id) in cart:
        del cart[str(product_id)]
        request.session['cart'] = cart

    return redirect('cart_view')


def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    return render(request, 'products/product_detail.html', {'product': product})

def update_cart(request, product_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity'))
        cart = request.session.get('cart', {})
        if str(product_id) in cart:
            cart[str(product_id)]['quantity'] = quantity
            request.session['cart'] = cart
    return redirect('cart_view')

def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
        request.session['cart'] = cart
    return redirect('cart_detail')



