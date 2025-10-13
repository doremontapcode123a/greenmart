from django.shortcuts import render
from app.models import Product, Category, Order, User  
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate, login, logout
from app import models

def dashboard(request):
    product_count = Product.objects.count()
    category_count = Category.objects.count()
    order_count = Order.objects.count()
    user_count = User.objects.count()

    context = {
        'product_count': product_count,
        'category_count': category_count,
        'order_count': order_count,
        'user_count': user_count,
    }
    return render(request, 'dashboard.html', context)



def product_list(request):
    products = Product.objects.all().order_by('-created_at')
    return render(request, 'product.html', {'products': products})

def order_list(request):
    orders = Order.objects.all().order_by('-date_order')
    return render(request, 'orders.html', {'orders': orders})

@user_passes_test(lambda u: u.is_staff)
def user_list(request):
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'users.html', {'users': users})

@user_passes_test(lambda u: u.is_staff)
def toggle_user_status(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_active = not user.is_active
    user.save()
    status = "mở khóa" if user.is_active else "khóa"
    messages.success(request, f"Tài khoản {user.username} đã được {status}.")
    return redirect('admin_users')

def admin_login(request):

    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_dashboard')

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_staff: 
            login(request, user)
            return redirect('admin_dashboard')
        else:
            messages.error(request, "Tên đăng nhập hoặc mật khẩu không hợp lệ!")

    return render(request, "loginn.html")

def logout_view(request):
    logout(request)
    return redirect("loginn")

def add_product(request):
    categories = Category.objects.all()
    
    
    if request.method == "POST":
        print("📩 Đã vào view add_product")
        name = request.POST.get('name')
        category_id = request.POST.get('category')
        price = request.POST.get('price')
        unit = request.POST.get('unit')
        origin = request.POST.get('origin')
        stock = request.POST.get('stock')
        status = request.POST.get('status')
        description = request.POST.get('description')
        image = request.FILES.get('image')
        is_featured = request.POST.get('is_featured') == 'on'
        
        

        try:
            category = Category.objects.get(id=category_id)
            product = Product.objects.create(
                name=name,
                category=category,
                description=description,
                price=price,
                unit=unit,
                stock=stock,
                status=status,
                origin=origin,
                image=image,
                is_featured=is_featured,
            )
            print(f"Tạo sản phẩm: {name}, category={category_id}, price={price}")
            product.save()
            messages.success(request, f"✅ Sản phẩm '{product.name}' đã được thêm thành công!")
            return redirect("admin_products")

        except Category.DoesNotExist:
            messages.error(request, "❌ Danh mục không hợp lệ!")
        except Exception as e:
            messages.error(request, f"⚠️ Lỗi: {e}")
        

    return render(request, "AddProduct.html", {"categories": categories})


def edit_product(request, slug):
    categories = Category.objects.all()
    product = Product.objects.get(slug = slug)
    
    
    if request.method == "POST":
        
        name = request.POST.get('name')
        category_id = request.POST.get('category')
        price = request.POST.get('price')
        unit = request.POST.get('unit')
        origin = request.POST.get('origin')
        stock = request.POST.get('stock')
        status = request.POST.get('status')
        description = request.POST.get('description')
        image = request.FILES.get('image')
        is_featured = request.POST.get('is_featured') == 'on'
        if image is None:
            image = product.image
        
        

        try:
            category = Category.objects.get(id=category_id)
            product.name = name
            product.category = category
            product.description = description
            product.price = price
            product.unit = unit
            product.stock = stock
            product.status = status
            product.origin = origin
            product.is_featured = is_featured
            product.image = image
     
            product.save()
            messages.success(request, f"✅ Sản phẩm '{product.name}' đã được sửa thành công!")
            return redirect("admin_products")

        except Category.DoesNotExist:
            messages.error(request, "❌ Danh mục không hợp lệ!")
        except Exception as e:
            messages.error(request, f"⚠️ Lỗi: {e}")
    return render(request, 'editProduct.html', {"categories": categories, "product":product})


def delete_product(request, slug):
    product = Product.objects.get(slug = slug)
    product.delete()
    return redirect("admin_products")