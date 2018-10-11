from django.shortcuts import render, redirect, get_object_or_404
from couponBank.forms import UserForm, UserProfileForm, ProductForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.urls import reverse
from django.utils import timezone
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, QueryDict
from .models import User, UserProfile, Product, Order
from django.views.decorators.csrf import csrf_exempt
import io
import os
from google.oauth2 import service_account
from google.cloud import vision
from google.cloud.vision import types

credentials = service_account.Credentials. from_service_account_file('/Users/waikawongsitu/wdi/testing/.env/recognizion-a609ecd9ea34.json')
client = vision.ImageAnnotatorClient(credentials=credentials)

def homepage(request):
    return render(request, 'couponBank/homepage.html')

@login_required
def profile(request):
    return render(request, 'couponBank/profile.html')

def about(request):
    return render(request, 'couponBank/about.html')

def FAQ(request):
    return render(request, 'couponBank/FAQ.html')

@login_required
def shoppingCart(request):
    return render(request, 'couponBank/shoppingCart.html')

def detect_logos(path):
    """Detects logos in the file."""
    with io.open(path, 'rb') as image_file:
        content = image_file.read()
    image = vision.types.Image(content=content)
    response = client.logo_detection(image=image)
    logos = response.logo_annotations
    print('Logos:')
    return (logos[0].description)

def detect_text(path):
    """Detects text in the file."""
    with io.open(path, 'rb') as image_file:
        content = image_file.read()
    image = vision.types.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations
    print('Texts:')
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

@login_required
def create_product(request):
    user = User.objects.get(id=request.user.id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            try:
                picture = request.POST['picture']
                product.brand = detect_logos(picture)
                product.description = detect_text(picture)
                product.posted_at = timezone.datetime.now()
                product.user = request.user
            except:
                return redirect('profile')
            product.save()
            return redirect('profile')
        else:
            print('\nform is invalid\n')
    else:
        form = ProductForm()
    return render(request,'couponBank/createProduct.html', {'form': form },{'user': user})
