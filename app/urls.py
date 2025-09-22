from django.urls import path
from . import views
urlpatterns = [
    path('', views.home, name='home'),
    path('checkout/', views.checkout, name='checkout'),
    path('cart/', views.cart, name='cart'),
    path('loginn/', views.loginn, name= "loginn"),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name="register"),
    path('product/', views.product, name='product'),
    path('detail/<slug:slug>', views.detail, name='detail' ),
    path('search', views.search, name='search'),
    path('add-to-cart/<slug:slug>', views.add_to_cart, name="add_to_cart" )
]
