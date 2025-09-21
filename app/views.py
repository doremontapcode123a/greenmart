from django.shortcuts import render,redirect
from .models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import HttpResponse

# Create your views here.
def home(request):
    products = Product.objects.all()
    return render(request,"index.html",{'products':products})

def cart(request):
    return render(request, "cart.html")


def checkout(request):
    return render(request, "checkout.html")

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