from django.shortcuts import render,redirect
from sympy import re
from .models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import HttpResponse, get_object_or_404
from django.http import JsonResponse, Http404
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, login_required
import re
from django.db import transaction
from django.views.decorators.http import require_POST

def home(request):
    products = Product.objects.filter(is_featured = True)

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
    if request.user.is_authenticated:
        order, created = Order.objects.get_or_create(
            customer=request.user,
            complete=False
        )
    else:
        if not request.session.session_key:
            request.session.create()

        session_key = request.session.session_key

        order, created = Order.objects.get_or_create(
            transaction_id=session_key,
            complete=False
        )

    products = order.orderitem_set.all()
    

    products = order.orderitem_set.all()
    total_items = order.get_cart_items
    total_money = order.get_cart_total
    promotions = Promotion.objects.all()
    order_items = order.orderitem_set.all()

    for item in order_items:
        if item.product.status == "hidden":
            item.delete()
    return render(request, "cart.html", {
        "order":order,
        "products": products,
        "total_items": total_items,
        "total_money": total_money,
        
    })


@login_required
def checkout(request):
    order = get_cart(request)

    if not order.orderitem_set.exists():
        messages.warning(request, "Giỏ hàng đang trống.")
        return redirect('cart')  # đổi thành tên url của trang giỏ hàng

    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    products = order.orderitem_set.all()

    if order.promotion:
        total_money = order.get_total_after_discount
    else:
        total_money = order.get_cart_total
    discount_amount = order.get_cart_total - total_money

    return render(request, "checkout.html", {
        "order": order,
        "discount_amount": discount_amount,
        "products": products,
        "profile": profile,
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
            messages.error(request,"Tên đăng nhập không được chứa dấu hoặc khoảng trắng")
            return redirect('register')
        if User.objects.filter(email=email).exists():
            messages.error(request,"Email đã tồn tại")
            return redirect('register')
        if User.objects.filter(username=username).exists():
            messages.error(request,"Tên đăng nhập đã tồn tại")
            return redirect('register')
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            messages.error(request,"Tên đăng nhập không được chứa dấu hoặc khoảng trắng")
            return redirect('register')

        if not re.match(r'^[\x00-\x7F]+$', password) or " " in password:
            messages.error(request,"Mật khẩu không được chứa dấu hoặc khoảng trắng")
            return redirect('register')
        user = User.objects.create_user(username = username, email=email, password=password)
        user.save()

        return redirect('loginn')
    return render(request, "register.html")


def detail(request, slug):
    product = Product.objects.get(slug = slug)
    categories = Category.objects.all()
    reviews = product.reviews.filter(parent__isnull=True).order_by('-created_at')
    if request.user.is_authenticated:
        # Giỏ hàng cho user đã login
        order, created = Order.objects.get_or_create(customer=request.user, complete=False)
    else:
    
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key

        order, created = Order.objects.get_or_create(transaction_id=session_key, complete=False)

    cartItems = order.get_cart_items if order else 0
    
    return render(request, 'detail.html', {'product':product,"categories":categories,'items':cartItems,'reviews':reviews})


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

def get_cart(request):
    if request.user.is_authenticated:
        order, _ = Order.objects.get_or_create(
            customer=request.user,
            complete=False,
        )
    else:
        if not request.session.session_key:
            request.session.create()
        order, _ = Order.objects.get_or_create(
            transaction_id=request.session.session_key,
            customer=None,
            complete=False,
        )
        request.session['guest_order_id'] = order.id
    return order


def add_to_cart(request, slug):
    product = get_object_or_404(Product, slug=slug)
    order = get_cart(request)

    order_item, _ = OrderItem.objects.get_or_create(order=order, product=product)
    order_item.quantity += 1
    order_item.save()

    messages.success(request, f"✅ {product.name} đã được thêm vào giỏ hàng!")

    return redirect(request.META.get('HTTP_REFERER', '/'))

def add_to_cart_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    if request.method == "POST":
       quantity = request.POST.get("quantity")

    if request.user.is_authenticated:
        order, created = Order.objects.get_or_create(customer=request.user, complete=False)
    else:
        # Nếu chưa login thì tạm cho order None (hoặc redirect login)
        order, created = Order.objects.get_or_create(customer=None, complete=False)

    order_item, created = OrderItem.objects.get_or_create(order=order, product=product)
    order_item.quantity += int(quantity)
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
    products = Product.objects.filter(
    status="available"
)
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
    promotions = Promotion.objects.filter(is_active=True)
    order = get_cart(request)
    return render(request, 'promotions_list.html', {
        'promotions': promotions,
        'order': order,
    })


def cancel_promotion(request, promo_id):
    order = get_cart(request)
    order.promotion = None
    order.discount_amount = 0
    order.total_after_discount = order.get_cart_total
    order.save()
    return redirect('cart')


def use_promotion(request, promo_id):
    promo = get_object_or_404(Promotion, id=promo_id, is_active=True)
    order = get_cart(request)

    cart_total = order.get_cart_total

    if not order.orderitem_set.exists():
        messages.warning(request, "Giỏ hàng đang trống, chưa thể áp dụng mã.")
        return redirect('cart')

    if cart_total < promo.min_order_value:
        messages.warning(request, "Đơn hàng chưa đạt giá trị tối thiểu để áp dụng mã này.")
        return redirect('cart')

    if promo.discount_type == 'money':
        discount = promo.discount_value
    else:
        discount = cart_total * promo.discount_value / 100

    discount = min(discount, cart_total)  # không giảm quá tổng tiền

    order.promotion = promo
    order.discount_amount = discount
    order.total_after_discount = cart_total - discount
    order.save()

    messages.success(
        request,
        f"🎉 Đã áp dụng mã '{promo.code}' thành công! "
        f"Giảm {promo.discount_value}{'%' if promo.discount_type == 'percent' else 'đ'}."
    )
    return redirect('cart')

@login_required
def add_review(request, slug):
    product = get_object_or_404(Product, slug=slug)
    if request.method == 'POST':
        rating = int(request.POST.get('rating', 0))
        comment = request.POST.get('comment', '').strip()
        if rating < 1 or rating > 5:
            messages.error(request, "Số sao phải từ 1 đến 5.")
        elif not comment:
            messages.error(request, "Vui lòng nhập nội dung đánh giá.")
        else:
            Review.objects.create(
                product=product,
                user=request.user,
                rating=rating,
                comment=comment
            )
            messages.success(request, "Đánh giá của bạn đã được gửi thành công!")
    return redirect('detail', product.slug)


@login_required
def reply_review(request, review_id):
    parent_review = get_object_or_404(Review, id=review_id)
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Review.objects.create(
                product=parent_review.product,
                user=request.user,
                comment=content,
                parent=parent_review
            )
    return redirect('detail', slug=parent_review.product.slug)

def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        profile.full_name = request.POST.get('full_name')
        profile.phone = request.POST.get('phone')
        profile.address = request.POST.get('address')
        profile.save()
        messages.success(request, "✅ Cập nhật thông tin thành công!")
        return redirect('profile')

    return render(request, 'profile.html', {'profile': profile})\
    


def complete_cart(request):
    order = Order.objects.filter(
        customer=request.user,
        complete=False
    ).first()

    if not order:
        return render(request, "complete.html", {
            "order": None
        })

    # Lấy tiền TRƯỚC khi complete order
    if order.promotion:
        total_money = order.get_total_after_discount
    else:
        total_money = order.get_cart_total

    # Lưu trạng thái đơn hàng
    order.complete = True
    order.save()

    return render(request, "complete.html", {
        "order": order,
        "total_money": total_money,
    })

def policy(request):
    return render(request, "policy.html")