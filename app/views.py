from django.shortcuts import render,redirect
from .models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import HttpResponse, get_object_or_404
from django.http import JsonResponse, Http404
from django.contrib import messages
# Create your views here.
def home(request):
    products = Product.objects.all()

    if request.user.is_authenticated:
        # Giỏ hàng cho user đã login
        order, created = Order.objects.get_or_create(customer=request.user, complete=False)
    else:
        # Giỏ hàng cho khách vãng lai
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key

        order, created = Order.objects.get_or_create(transaction_id=session_key, complete=False)

    cartItems = order.get_cart_items if order else 0

    return render(request, "index.html", {
        'products': products,
        "items": cartItems
    })

def cart(request):
    
    order = Order.objects.filter(customer=request.user, complete=False).first()
    
    if not order:
        
        order = Order.objects.create(customer=request.user, complete=False)

    products = order.orderitem_set.all()
    total_items = order.get_cart_items
    total_money = order.get_cart_total
    
    return render(request, "cart.html", {
        "products": products,
        "total_items": total_items,
        "total_money": total_money,
    })


def checkout(request):
    order = Order.objects.filter(customer=request.user, complete=False).first()
    
    if not order:
        
        order = Order.objects.create(customer=request.user, complete=False)

    products = order.orderitem_set.all()
    total_items = order.get_cart_items
    total_money = order.get_cart_total
    
    return render(request, "checkout.html", {
        "products": products,
        "total_items": total_items,
        "total_money": total_money,
    })
    

def loginn(request):
    if request.method == 'POST':
        fnm = request.POST.get("fnm")
        pwd = request.POST.get('password')
        user = authenticate(request, username = fnm, password = pwd)
        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            return redirect("loginn")
        
    return render(request, "login.html")

def product(request):
    return render(request, "products.html")

def register(request):
    if request.method == "POST":
        username = request.POST.get('fnm')
        email = request.POST.get('email')
        password = request.POST.get("pwd")
        pwd2 = request.POST.get('pwd1')
        if pwd2 != password:
            return HttpResponse("mat khau khong khop vui long nhap lai")
        user = User.objects.create_user(username = username, email=email, password=password)
        user.save()
        return redirect('loginn')
    return render(request, "register.html")


def detail(request, slug):
    product = Product.objects.get(slug = slug)
    return render(request, 'detail.html', {'product':product})


def search(request):
    if request.method == "GET":
        query = request.GET.get('q', '').strip()  
        products = Product.objects.none()  
        if query:
            products = Product.objects.filter(name__icontains=query)
        return render(request, 'search.html', {
            'query': query,
            'products': products
        })

def add_to_cart(request, slug):
    product = get_object_or_404(Product, slug=slug)

    if request.user.is_authenticated:
        order, created = Order.objects.get_or_create(customer=request.user, complete=False)
    else:
        # Nếu chưa login thì tạm cho order None (hoặc redirect login)
        order, created = Order.objects.get_or_create(customer=None, complete=False)

    order_item, created = OrderItem.objects.get_or_create(order=order, product=product)
    order_item.quantity += 1
    order_item.save()

    messages.success(request, f"✅ {product.name} đã được thêm vào giỏ hàng!")

    return redirect('home')

def logout_view(request):
    logout(request)
    return redirect("loginn")