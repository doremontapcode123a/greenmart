from django.shortcuts import render,redirect
from .models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import HttpResponse, get_object_or_404
from django.http import JsonResponse, Http404
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test

# Create your views here.
def home(request):
    products = Product.objects.all()

    if request.user.is_authenticated:
        # Giỏ hàng cho user đã login
        order, created = Order.objects.get_or_create(customer=request.user, complete=False)
    else:
    
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
    promotions = Promotion.objects.all()
    
    return render(request, "cart.html", {
        "order":order,
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
    if order.promotion :
        total_money = order.get_total_after_discount
        money = order.get_cart_total - order.get_total_after_discount
    else:
        total_items = order.get_cart_total
    
  
    return render(request, "checkout.html", {
        "order":order,
        "discount_amount":money,
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
    categories = Category.objects.all()
    if request.user.is_authenticated:
        # Giỏ hàng cho user đã login
        order, created = Order.objects.get_or_create(customer=request.user, complete=False)
    else:
    
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key

        order, created = Order.objects.get_or_create(transaction_id=session_key, complete=False)

    cartItems = order.get_cart_items if order else 0
    
    return render(request, 'detail.html', {'product':product,"categories":categories,'items':cartItems})


def search(request):
    if request.method == "GET":
        query = request.GET.get('q', '').strip()  
        products = Product.objects.none()  
        if request.user.is_authenticated:
        # Giỏ hàng cho user đã login
            order, created = Order.objects.get_or_create(customer=request.user, complete=False)
        else:
            if not request.session.session_key:
                request.session.create()
            session_key = request.session.session_key
            order, created = Order.objects.get_or_create(transaction_id=session_key, complete=False)
        cartItems = order.get_cart_items if order else 0
        if query:
            products = Product.objects.filter(name__icontains=query)
        return render(request, 'search.html', {
            'query': query,
            'products': products,
            'items':cartItems
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

    return redirect(request.META.get('HTTP_REFERER', '/'))

def arrow_up(request, slug):
    product = get_object_or_404(Product, slug=slug)

    if request.user.is_authenticated:
        order, created = Order.objects.get_or_create(customer=request.user, complete=False)
    else:
        # Nếu chưa login thì tạm cho order None (hoặc redirect login)
        order, created = Order.objects.get_or_create(customer=None, complete=False)

    order_item, created = OrderItem.objects.get_or_create(order=order, product=product)
    order_item.quantity += 1
    order_item.save()


    return redirect("cart")

def arrow_down(request, slug):
    product = get_object_or_404(Product, slug=slug)

    if request.user.is_authenticated:
        order, created = Order.objects.get_or_create(customer=request.user, complete=False)
    else:
        # Nếu chưa login thì tạm cho order None (hoặc redirect login)
        order, created = Order.objects.get_or_create(customer=None, complete=False)
    

    order_item, created = OrderItem.objects.get_or_create(order=order, product=product)
    order_item.quantity -= 1
    if(order_item.quantity <= 0):
        order_item.delete()
    else:
        order_item.save()


    return redirect("cart")

def logout_view(request):
    logout(request)
    return redirect("loginn")


def productPage(request):
    categories = Category.objects.all()
    products = Product.objects.all()
    if request.user.is_authenticated:
        # Giỏ hàng cho user đã login
        order, created = Order.objects.get_or_create(customer=request.user, complete=False)
    else:
    
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key

        order, created = Order.objects.get_or_create(transaction_id=session_key, complete=False)

    cartItems = order.get_cart_items if order else 0

    return render(request, "productPage.html",{"categories":categories, "products":products,"items":cartItems})



@user_passes_test(lambda u: u.is_staff)
def dashboard(request):
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    total_revenue = sum(o.get_cart_total for o in Order.objects.filter(complete=True))
    context = {
        "total_products": total_products,
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "recent_orders": Order.objects.order_by("-date_order")[:5],
    }
    return render(request, "admin.html", context)



def promotion_list(request):
    user = request.user
    promotions = user.promotions.all()
 
    return render(request, 'promotions_list.html', {'promotions': promotions})



def use_promotion(request, promo_id):
    promo = get_object_or_404(Promotion, id=promo_id, is_active=True)
    user = request.user


    order = Order.objects.filter(customer=user, complete=False).first()
    if not order:
        messages.error(request, "Không tìm thấy đơn hàng để áp dụng khuyến mãi.")
        return redirect('cart')


    if order.get_cart_total < promo.min_order_value:
        messages.warning(request, "Đơn hàng chưa đạt giá trị tối thiểu để áp dụng mã này.")
        return redirect('cart')

 
    if promo.discount_type == 'money':
        discount = promo.discount_value
    else:
        discount = order.get_cart_total * promo.discount_value / 100

    new_total = max(order.get_cart_total - discount, 0)

  
    order.promotion = promo
    order.discount_amount = discount
    order.total_after_discount = new_total
    order.save()

    messages.success(request, f"🎉 Đã áp dụng mã '{promo.code}' thành công! Giảm {promo.discount_value}{'%' if promo.discount_type == 'percent' else 'đ'}.")

    return redirect('cart')