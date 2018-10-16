from django.contrib import admin
from .models import UserProfile, Product, Order, Transaction, Reviews
# Register your models here.

admin.site.register(UserProfile)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(Transaction)
admin.site.register(Reviews)