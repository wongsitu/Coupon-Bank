
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.urls import reverse
from django.utils import timezone
from django.db.models import Q
from django.http import HttpResponse
from django.template.loader import get_template
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from couponBank.forms import UserForm, UserProfileForm, ProductForm, ReviewForm
from .models import User, UserProfile, Product, Order, Transaction, Reviews
from google.oauth2 import service_account
from google.cloud import vision
from google.cloud.vision import types
import stripe
import io
from io import BytesIO
import os
import random, string
import json
from xhtml2pdf import pisa
from threading import Timer
import random
from celery import task
import requests

credentials_raw = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')

service_account_info = json.loads(credentials_raw)

credentials = service_account.Credentials.from_service_account_info(service_account_info)

client = vision.ImageAnnotatorClient(credentials=credentials)

@task
def dealOfDay(request):
    deal = Product.objects.all().last()
    return deal

def homepage(request):
    deal = dealOfDay(request)
    random_items = random.sample(list(Product.objects.all()), k=5)
    content ={
        'random_items': random_items,
        'deal':deal
    }
    return render(request, 'couponBank/homepage.html', content)

def store_page(request):
    products = Product.objects.all()
    paginator = Paginator(products,8)
    page = request.GET.get('page')
    products = paginator.get_page(page)
    return render(request, 'couponBank/store_page.html',{'products': products })

@login_required
def profile(request):
    user = User.objects.get(id=request.user.id)
    user_profile , created = UserProfile.objects.get_or_create(user=user)
    user_offers = Product.objects.filter(user=user)
    user_orders = Transaction.objects.filter(profile=user_profile)
    pending_orders = Order.objects.filter(is_ordered=True).filter(products__user=user)
    content = {
        'user_offers': user_offers,
        'user_orders':user_orders, 
        'user_profile':user_profile, 
        'pending_orders':pending_orders 
        }
    return render(request, 'couponBank/profile.html', content)

@login_required
def edit_profile(request):
    user = User.objects.get(id=request.user.id)
    user , created = UserProfile.objects.get_or_create(user=user)
    user.save()
    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save()
            if 'profile_pic' in request.FILES:
                user.profile_pic = request.FILES['profile_pic']
            user.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user)
    content = {
        'form': form,
        'user': user,
        }
    return render(request, 'couponBank/edit_profile.html', content)

def search(request):
    query = request.GET.get('q')
    searched_products = Product.objects.filter(Q(brand__icontains=query)|Q(description__icontains=query))
    content = {
        'searched_products': searched_products 
        }
    return render(request, 'couponBank/searchpage.html',content)

def about(request):
    return render(request, 'couponBank/about.html')

def FAQ(request):
    return render(request, 'couponBank/FAQ.html')

def coupon_bank_eats(request):
    headers = {"Authorization" : "Bearer " + settings.YELP_API_KEY}
    response = requests.get("https://api.yelp.com/v3/businesses/WavvLdfdP6g8aZTtbBQHTw",headers=headers)
    content = {
        'response': response
    }
    return render(request, 'couponBank/coupon_bank_eats.html',content)

@login_required
def shoppingCart(request):
    user = User.objects.get(id=request.user.id)
    cart_orders = Order.objects.filter(buyer=user, is_ordered=False)
    Total_price = 0
    for order in cart_orders:
        Total_price = Total_price + order.products.price
    content = {
        "cart_orders":cart_orders,
        "Total_price":Total_price
        }
    return render(request, 'couponBank/shoppingCart.html', content)

def detect_logos(uri):
    image = vision.types.Image()
    image.source.image_uri = uri
    response = client.logo_detection(image=image)
    logos = response.logo_annotations
    try:
        logo = logos[0].description
    except IndexError:
        logo = None
    return (logo)

def detect_text(uri):
    image = vision.types.Image()
    image.source.image_uri = uri
    response = client.text_detection(image=image)
    texts = response.text_annotations
    description = []
    for text in texts:
        description.append(text.description)
    try:
        descript = description[0]
    except IndexError:
        descript = None
    return(descript)

def random_generator(size=12, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request,user)
                messages.success(request, 'You have logged in successfully')
                return redirect('homepage')
            else:
                messages.warning(request,"Your account was inactive.")
                return redirect('user_login')
        else:
            messages.warning(request,"Invalid login details given")
            return redirect('user_login')
    else:
        return render(request, 'couponBank/login.html')

def register(request):
    registered = False
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        if user_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            messages.success(request, 'Thanks for joining')
            registered = True
            login(request, user)
            return redirect('homepage')
        else:
            print(user_form.errors)
    else:
        user_form = UserForm()
    return render(request, 'couponBank/registration.html', {'user_form':user_form,'registered':registered})

@login_required
def user_logout(request):
    logout(request)
    messages.success(request, 'You have logged out')
    return redirect('homepage')

@login_required
def create_product(request):
    user = User.objects.get(id=request.user.id)
    userprofile, status = UserProfile.objects.get_or_create(user=user)
    if userprofile.phone == None or userprofile.country == None or userprofile.address == None or userprofile.zipcode == None:
        messages.warning(request, 'You need to insert your profile information before posting a product')
    else:
        if request.method == 'POST':
            form = ProductForm(request.POST, request.FILES)
            if form.is_valid():
                product = form.save(commit=False)
                product.user = request.user
                product.posted_at = timezone.datetime.now()
                if 'picture' in request.FILES:
                    picture = request.FILES['picture']
                    product.save()
                    path = 'https://s3-us-west-1.amazonaws.com/' + settings.AWS_STORAGE_BUCKET_NAME + '/media/media/picture/' + str(picture)
                    product.brand = detect_logos(path)
                    product.description = detect_text(path)
                    if product.brand == None or product.description == None:
                        messages.warning(request,"Coupon is not valid")
                        return render(request,'couponBank/createProduct.html', {'form': form ,'user': user})
                    product.save()
                    messages.success(request, 'Your product has been posted')
            else:
                messages.error(request, 'Error')
    form = ProductForm()
    return render(request,'couponBank/createProduct.html', {'form': form,'user': user})

@login_required
def delete_product(request,pk):
    product_to_delete = Product.objects.get(id=pk)
    messages.success(request, "You {} coupon has been removed".format(product_to_delete))
    product_to_delete.delete()
    return redirect('profile')

def product_detail(request,pk):
    product = Product.objects.get(id=pk)
    reviews = Reviews.objects.filter(product=product.id)
    if request.user.is_authenticated:
        form = ReviewForm(request.POST)
        currently_log = User.objects.get(id=request.user.id)
        content = {
            'product': product,
            'reviews':reviews, 
            'currently_log':currently_log, 
            'form': form
            }
        return render(request,'couponBank/product_detail.html', content)
    return render(request,'couponBank/product_detail.html', {'product': product,'reviews':reviews})
    
def generate_order_id():
    date_str = str(timezone.datetime.now())
    return date_str

def add_to_cart(request,pk):
    if not request.user.is_anonymous:
        user = User.objects.get(id=request.user.id)
        product = Product.objects.get(id=pk)
        name = product.brand
        if product.user == user:
            messages.info(request,"It's your own product")
            return redirect('store_page')
        order = Order.objects.create(ref_code=generate_order_id(), buyer=user, is_ordered=False, products=product, date_ordered = timezone.datetime.now())
        order.save()
        messages.success(request,'Successfully added {} coupon to cart'.format(name))
        return redirect(request.META['HTTP_REFERER'])
    else:
        messages.info(request,"Please register or login to add to add this product")
        return redirect(request.META['HTTP_REFERER'])

@login_required
def delete_from_cart(request,pk):
    item_to_delete = Order.objects.get(id=pk)
    if item_to_delete != None:
        item_to_delete.delete()
        messages.success(request,"Item has been deleted")
    return redirect('shoppingCart')

@login_required
def payment(request):
    user = User.objects.get(id=request.user.id)
    userprofile, status= UserProfile.objects.get_or_create(user=user)
    if userprofile.phone == None or userprofile.country == None or userprofile.address == None or userprofile.zipcode == None:
        messages.warning(request, 'You need to insert your profile information before making a pursache')
        return redirect('profile')
    orders = Order.objects.filter(buyer=user, is_ordered=False)
    Total_price = []
    for obj in orders.filter().all():
        Total_price.append(obj.products.price)
    pricing = sum(Total_price)
    Total_price = sum(Total_price*100)
    content = { 
        "stripe_key": settings.STRIPE_TEST_PUBLIC_KEY, 
        "orders":orders, 
        "Total_price":Total_price,
        "pricing":pricing 
        }
    return render(request, "couponBank/payment.html", content)

@login_required
def checkout(request):
    user = User.objects.get(id = request.user.id)
    profile = UserProfile.objects.get(user=user)
    cart_orders = Order.objects.filter(buyer=user, is_ordered=False)
    publishKey = settings.STRIPE_TEST_SECRET_KEY
    stripe.api_key = settings.STRIPE_TEST_SECRET_KEY
    Total_price = 0
    for order in cart_orders:
        Total_price = Total_price + order.products.price
    if request.method == 'POST':
        try:
            token = request.POST['stripeToken']
            charge = stripe.Charge.create(
                amount=round(100*Total_price),
                currency='usd',
                description='Example charge',
                source=token,
            )
            randId = random_generator()
            transaction = Transaction.objects.create(profile=profile,token=randId,amount=Total_price)
            transaction.orders.set(cart_orders)
            cart_orders.update(is_ordered=True)
            messages.success(request, "Successfully Pursached.")
            return redirect(reverse('profile'))
        except stripe.error.CardError as e:
            messages.info(request, "Your card has been declined.")
    context = {
        'order': cart_orders,
        'STRIPE_TEST_SECRET_KEY': publishKey
        }
    return render(request, 'shopping_cart/checkout.html', context)

@login_required
def detele_transaction(request,pk):
    transaction_to_delete = Transaction.objects.get(id=pk)
    if transaction_to_delete != None:
        transaction_to_delete.delete()
    return redirect('profile')

@login_required
def invoice(request,pk):
    user = User.objects.get(id = request.user.id)
    profile = UserProfile.objects.get(user=user)
    transaction = Transaction.objects.get(id=pk)
    content = {
        'transaction': transaction,
        'profile':profile,
        'user':user
        }
    return render(request,'couponBank/invoice.html',content)

@login_required
def review_create(request, pk):
    order = Product.objects.get(id=pk)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = order
            review.save()
            return redirect('product_detail', pk=order.id)
    else:
        form = ReviewForm()
    return render(request, 'couponBank/product_detail.html', {'form': form})

@login_required
def review_delete(request, id, pk):
    order = Product.objects.get(id=pk)
    Reviews.objects.get(id=id).delete()
    messages.success(request,"Review deleted")
    return redirect('product_detail', pk=order.pk)

@login_required
def review_edit(request, id, pk):
    review = Reviews.objects.get(id=id)
    order = Product.objects.get(id=pk)
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            review = form.save()
            return redirect('product_detail', pk=order.id)
    else:
        form = ReviewForm(instance=review)
    return render(request, 'couponBank/product_detail.html', {'form': form})

def render_to_pdf(path: str, params: dict):
        template = get_template(path)
        html = template.render(params)
        response = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), response)
        if not pdf.err:
            return HttpResponse(response.getvalue(), content_type='application/pdf')
        else:
            return HttpResponse("Error Rendering PDF", status=400)

@login_required
def pdf_invoice_view(request,pk):
    user = User.objects.get(id = request.user.id)
    profile = UserProfile.objects.get(user=user)
    transaction = Transaction.objects.get(id=pk)
    results = {
        'transaction': transaction,
        'profile':profile,
        'user':user
        }
    return render_to_pdf( 'couponBank/pdf_invoice.html', {'pagesize':'A4', 'results': results})