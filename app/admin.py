from django.contrib import admin
from .models import Category, Product,OrderItem, Order, Promotion, UserProfile
# Register your models here.
# admin.site.register(Category)
# admin.site.register(Product)
# admin.site.register(OrderItem)
# admin.site.register(Order)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "unit", "stock", "status", "origin", "is_featured")
    list_filter = ("category", "status", "origin")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "date_order", "complete", "get_cart_total")
    list_filter = ("complete",)
    readonly_fields = ("transaction_id",)

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("product", "order", "quantity", "date_added")

admin.site.register(Promotion)
admin.site.register(UserProfile)