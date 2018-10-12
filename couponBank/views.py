from django.shortcuts import render, redirect, get_object_or_404
from couponBank.forms import UserForm, UserProfileForm, ProductForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.urls import reverse
from django.utils import timezone
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, QueryDict
from .models import User, UserProfile, Product, Order
from django.views.decorators.csrf import csrf_exempt
import io
import os
from google.oauth2 import service_account
from google.cloud import vision
from google.cloud.vision import types
from django.conf import settings

credentials = service_account.Credentials. from_service_account_file('/Users/waikawongsitu/wdi/testing/.env/recognizion-a609ecd9ea34.json')
client = vision.ImageAnnotatorClient(credentials=credentials)

def homepage(request):
    products = Product.objects.all()
    return render(request, 'couponBank/homepage.html',{'products': products })

@login_required
def profile(request):
    user = User.objects.get(id=request.user.id)
    user_offers = Product.objects.filter(user=user)
    return render(request, 'couponBank/profile.html',{'user_offers': user_offers })

def search(request):
    query = request.GET.get('q')
    searched_products = Product.objects.filter(Q(brand__icontains=query)|Q(description__icontains=query))
    return render(request, 'couponBank/searchpage.html',{'searched_products': searched_products })

def about(request):
    return render(request, 'couponBank/about.html')

def FAQ(request):
    return render(request, 'couponBank/FAQ.html')

@login_required
def shoppingCart(request):
    user = User.objects.get(id=request.user.id)
    cart_orders = Order.objects.filter(buyer=user)
    return render(request, 'couponBank/shoppingCart.html',{'cart_orders': cart_orders })

def detect_logos(path):
    """Detects logos in the file."""
    with io.open(path, 'rb') as image_file:
        content = image_file.read()
    image = vision.types.Image(content=content)
    response = client.logo_detection(image=image)
    logos = response.logo_annotations
    return (logos[0].description)

def detect_text(path):
    """Detects text in the file."""
    with io.open(path, 'rb') as image_file:
        content = image_file.read()
    image = vision.types.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations
    description = []
    for text in texts:
        description.append(text.description)
    return(description[0])

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request,user)
                return redirect('homepage')
            else:
                return HttpResponse("Your account was inactive.")
        else:
            print("Someone tried to login and failed.")
            print(f'They used username: {username} and password: {password}')
            return HttpResponse("Invalid login details given")
    else:
        return render(request, 'couponBank/login.html', {})

def register(request):
    registered = False
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        if user_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            registered = True
        else:
            print(user_form.errors)
    else:
        user_form = UserForm()
    return render(request, 'couponBank/registration.html', {'user_form':user_form,'registered':registered})

@login_required
def user_logout(request):
    logout(request)
    return redirect('homepage')

def get_user_pending_order(request):
    user = User.objects.get(id=request.user.id)
    order = Order.objects.filter(user=user, is_ordered=False)
    print(order)
    if order:
        print("Aloha")
        return order[0]
    return None

@login_required
def create_product(request):
    user = User.objects.get(id=request.user.id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.user = request.user
            product.posted_at = timezone.datetime.now()
            if 'picture' in request.FILES:
                picture = request.FILES['picture']
                product.save()
                path = "/Users/waikawongsitu/wdi/testing/couponBank/media/picture/"+str(picture)
                product.brand = detect_logos(path)
                product.description = detect_text(path)
                product.save()
        else:
            print('\nform is invalid\n')
    else:
        form = ProductForm()
    return render(request,'couponBank/createProduct.html', {'form': form },{'user': user})

@login_required
def delete_product(request,pk):
    product_to_delete = Product.objects.get(id=pk)
    product_to_delete.delete()
    return redirect('profile')

def product_detail(request,pk):
    product = Product.objects.get(id=pk)
    return render(request,'couponBank/product_detail.html', {'product': product})

def generate_order_id():
    date_str = str(timezone.datetime.now())
    return date_str

@login_required
def add_to_cart(request,pk):
    user = User.objects.get(id=request.user.id)
    product = Product.objects.get(id=pk)
    order, status = Order.objects.get_or_create(buyer=user,is_ordered=False,date_ordered=timezone.datetime.now())
    order.products.add(Product.objects.get(id=pk))
    if status:
        order.ref_code = generate_order_id()
        order.save()
    print(order.get_cart_items())
    print("Item added to cart")
    return redirect('homepage')

@login_required
def delete_from_cart(request,pk):
    item_to_delete = Order.objects.get(id=pk)
    if item_to_delete.exist():
        item_to_delete.delete()
        print("Item has been deleted")
    return redirect('profile')

@login_required
def order_details(request,id):
    existing_order = get_user_pending_order(request)
    context = {
        'order': existing_order
    }
    return render(request,"couponBank/summary.html",context)

@login_required
def checkout(request):
    existing_order = get_user_pending_order(request)
    context ={
        'order': existing_order
    }
    return render(request, 'couponBank/checkout.html',context)

@login_required
def payment(request):
    context = { "stripe_key": settings.STRIPE_PUBLIC_KEY }
    return render(request, "couponBank/payment.html", context)


