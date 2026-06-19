from django.db import models
from django.conf import settings
from django.core.validators import MinLengthValidator

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(
        upload_to='categories/',
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products'
    )
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(
        max_digits=18,
        decimal_places=2
    )
    quantity = models.PositiveIntegerField(default=0)
    image = models.ImageField(
        upload_to='products/',
        null=True,
        blank=True
    )
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def image_default(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return f"{settings.STATIC_URL}images/default-product.jpg"
    
    def __str__(self):
        return self.name
    

class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='products/gallery/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.product.name}"

class Account(models.Model):
    fullname = models.CharField(max_length=100)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255, validators=[MinLengthValidator(6, message="Mật khẩu tối thiểu 6 ký tự")])
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True
    )
    role = models.CharField(
        max_length=10,
        default='USER'
    )
    status = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def avatar_default(self):
        if self.avatar and hasattr(self.avatar, 'url'):
            return self.avatar.url
        return f"{settings.STATIC_URL}images/default-avatar.jpg"

    def __str__(self):
        return self.username
    
class CartItem(models.Model):
    account = models.ForeignKey(
        'Account', 
        on_delete=models.CASCADE, 
        related_name='cart_items'
    )
    product = models.ForeignKey(
        'Product', 
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(default=1)
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cart_items'
        unique_together = ('account', 'product')

    def __str__(self):
        return f"Cart Account_{self.account_id} - {self.product.name}"