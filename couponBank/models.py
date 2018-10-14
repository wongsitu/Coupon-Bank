from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django_countries.fields import CountryField

# Userprofile
class UserProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='profile_pics',blank=True)
    phone = models.CharField(blank=True,max_length=50)
    country = CountryField(blank_label='(select country)',blank=True)
    address = models.CharField(blank=True,max_length=50)
    zipcode = models.CharField(blank=True,max_length=50)

    def __str__(self):
        return self.user.username

# An individual product
class Product (models.Model):
    brand = models.CharField(max_length=1000,blank=True)
    description = models.TextField(max_length=1000,blank=True)
    picture = models.ImageField(upload_to='picture/',blank=True)
    posted_at = models.DateTimeField()
    price = models.PositiveIntegerField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='products') #Many products to a user

    def __str__(self):
        return self.brand

# An individual order_item
class Order (models.Model): 
    ref_code = models.CharField(max_length=100)
    buyer = models.ForeignKey(User,on_delete=models.SET_NULL, null=True)
    is_ordered = models.BooleanField(default=False)
    products = models.ForeignKey(Product,on_delete=models.CASCADE,related_name='product') #Many products to an order
    date_ordered = models.DateTimeField()

    def __str__(self):
        return str(self.products)

class Transaction (models.Model):
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    token = models.CharField(max_length=120)
    orders = models.ManyToManyField(Order)
    amount = models.DecimalField(max_digits=100, decimal_places=2)
    success = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)

    def __str__(self):
        # return self.orders
        return str(self.orders)

