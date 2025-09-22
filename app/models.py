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
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    def save(self):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save()
    
class Order(models.Model):
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    date_order = models.DateTimeField(auto_now_add=True)
    complete =  models.BooleanField(default=False,null=True,blank=False)
    transaction_id = models.CharField(auto_created=True)
    
    
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

class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    @property
    def get_total(self):
        return self.product.price * self.quantity
    
    
    

