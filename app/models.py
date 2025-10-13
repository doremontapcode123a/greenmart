from datetime import timezone
import datetime
from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
# Create your models here.
from django.db import models
class Origin(models.TextChoices):
    VIETNAM = "VN", "Việt Nam"
    USA = "US", "Mỹ"
    AUSTRALIA = "AU", "Úc"
    JAPAN = "JP", "Nhật Bản"
    KOREA = "KR", "Hàn Quốc"
    THAILAND = "TH", "Thái Lan"
    OTHER = "OT", "Khác"



class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)   # Rau, Củ, Quả, Trái Cây, Nấm, ...
    slug = models.SlugField(max_length=100, blank=True)

    def __str__(self):
        return self.name
    def save(self):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save()


class Product(models.Model):
    UNIT_CHOICES = [
        ("kg", "Kilogram"),
        ("gr", "Gram"),
        ("bó", "Bó"),
        ("túi", "Túi"),
        ("quả", "Quả"),
    ]

    STATUS_CHOICES = [
        ("available", "Còn hàng"),
        ("out_of_stock", "Hết hàng"),
        ("hidden", "Ẩn"),
    ]

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank = True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    description = models.TextField(blank=True, null=True)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default="kg")
    stock = models.PositiveIntegerField(default=0)  # số lượng tồn kho
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="available")

    origin = models.CharField(max_length=100, choices=Origin.choices, default=Origin.VIETNAM, blank=True, null=True)   # Việt Nam, Úc, Mỹ...
    
    image = models.ImageField(upload_to="products/", blank=True, null=True)

    is_featured = models.BooleanField(default=False)   # Sản phẩm nổi bật
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank= True, null=True)

    def __str__(self):
        return self.name
    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
      if not self.slug:
        self.slug = slugify(self.name)
      super().save(force_insert=force_insert,
                 force_update=force_update,
                 using=using,
                 update_fields=update_fields)
    
class Order(models.Model):
    customer = models.ForeignKey(User, max_length=100, on_delete=models.SET_NULL, null=True, blank=True)
    date_order = models.DateTimeField(max_length=100,auto_now_add=True)
    complete =  models.BooleanField(default=False,null=True,blank=False)
    transaction_id = models.CharField(max_length=100, auto_created=True)
    promotion = models.ForeignKey(
        'Promotion', on_delete=models.SET_NULL, null=True, blank=True, related_name='orders'
    )
    
    def __str__(self):
        return str(self.id)
    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total
    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total
    
    @property
    def get_discount_amount(self):
        """Trả về số tiền giảm nếu có khuyến mãi"""
        if self.promotion:
            return self.promotion.get_discount(self.get_cart_total) 
        return 0

    @property
    def get_total_after_discount(self):
        """Tổng tiền sau khi áp khuyến mãi"""
        return self.get_cart_total - self.get_discount_amount

class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(max_length=100,auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    @property
    def get_total(self):
        return self.product.price * self.quantity
    
    
    
class UserProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile'
    )
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    address = models.TextField(max_length=100)

    def __str__(self):
        return f"Hồ sơ của {self.user.username}"
    

class Promotion(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('money', 'Giảm theo số tiền'),
        ('percent', 'Giảm theo phần trăm'),
    ]

    APPLY_TYPE_CHOICES = [
        ('product', 'Theo sản phẩm'),
        ('category', 'Theo danh mục'),
        ('order', 'Toàn đơn hàng'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="promotions")

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICES)
    discount_value = models.DecimalField(max_digits=100000000, decimal_places=2)
    apply_type = models.CharField(max_length=10, choices=APPLY_TYPE_CHOICES, default='order')

   
    products = models.ManyToManyField('Product', blank=True)
    categories = models.ManyToManyField('Category', blank=True)

    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    min_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.name} ({self.code})"

    def get_discount(self, order_total, order_items=None):
       
        if not self.is_active:
            return 0
        if order_total < self.min_order_value:
            return 0

        discount = 0
        if self.apply_type == 'order':
            if self.discount_type == 'money':
                discount = min(self.discount_value, order_total)
            elif self.discount_type == 'percent':
                discount = order_total * (self.discount_value / 100)
        elif self.apply_type == 'product' and order_items:
            for item in order_items:
                if item.product in self.products.all():
                    if self.discount_type == 'money':
                        discount += min(self.discount_value, item.get_total)
                    elif self.discount_type == 'percent':
                        discount += item.get_total * (self.discount_value / 100)
        elif self.apply_type == 'category' and order_items:
            for item in order_items:
                if item.product.category in self.categories.all():
                    if self.discount_type == 'money':
                        discount += min(self.discount_value, item.get_total)
                    elif self.discount_type == 'percent':
                        discount += item.get_total * (self.discount_value / 100)

        return round(discount, 2)