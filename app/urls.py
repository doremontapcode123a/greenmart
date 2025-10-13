from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
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
    path('add-to-cart/<slug:slug>', views.add_to_cart, name="add_to_cart" ),
    path('resert_password/', auth_views.PasswordResetView.as_view(template_name = "password_reset.html"), name = "reset_password"),
    path('resert_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name = "password_reset_done.html"), name="password_reset_done"),
    path('resert/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name = "password_reset_confirm.html"), name="password_reset_confirm"),
    path('resert_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name = "password_reset_complete.html"), name="password_reset_complete"),
    path("arrow_up/<slug:slug>", views.arrow_up, name='arrow_up' ),
    path("arrow_down/<slug:slug>", views.arrow_down, name='arrow_down' ),
    path("productPage/", views.productPage, name="productPage"),
    # path("applypromotions/", views.apply_promotion, name="promotions_list"),
    path('promotions/', views.promotion_list, name='promotion_list'),
    path('promotions/use/<int:promo_id>/', views.use_promotion, name='use_promotion'),


]
