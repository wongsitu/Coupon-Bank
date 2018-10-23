# Coupon Bank

Coupon Bank is a peer-to-peer lending aplication that allows users to buy and sell coupons. The motivation of this project was to create an exchange platform that would allow users to trade 'long tail' coupons.

Link: https://waikamazon.herokuapp.com/

# Images

![Alt text](https://github.com/wongsitu/Coupon-Bank/blob/master/assets/homepage.png)

![Alt text](https://github.com/wongsitu/Coupon-Bank/blob/master/assets/coupon1.png)

![Alt text](https://github.com/wongsitu/Coupon-Bank/blob/master/assets/coupon2.png)

![Alt text](https://github.com/wongsitu/Coupon-Bank/blob/master/assets/aboutpage.png)

![Alt text](https://github.com/wongsitu/Coupon-Bank/blob/master/assets/post_product.png)

![Alt text](https://github.com/wongsitu/Coupon-Bank/blob/master/assets/FAQ.png)

![Alt text](https://github.com/wongsitu/Coupon-Bank/blob/master/assets/profilepage.png)

## Features

- User authentication: Users are able to Log in, Log out and Register
- Google Cloud Vision API: When the users upload their coupons, GCVA will grab all the information from the coupon using visual recognition. This includdes the Logo and description. If the coupon is not valid, it will return an invalid message
- Stripe: Includes payment system that handles all transactions. It takes a pertentage of the total price as revenue for the website
- CRUD functionality: Users are able to create, read, update and delete reviews. Also they are able to create, read and delete coupons that were posted/ordered

## Technologies

- Front End: HTML, CSS, Bootstrap, Fontawesome
- Back End: Django 2.0+, Python 3.7.0, Javascript, jQuery
- APIs: Google Cloud API, Stripe
- Django modules: django countries, dj-stripe, Pillow

## Google Cloud Vision API

The hardest part of couponBank was to set up GCVA. First, You need to have a google account. Then you go to https://console.cloud.google.com/ and create a new project. You will be able to retrieve an json file that contains all your credentials. It should look something like this:

```json
    {
        "type": "service_account",
        "project_id": "marcanuy-XXXXXX",
        "private_key_id": "XXXXXXXXXXXXX",
        "private_key": "-----BEGIN PRIVATE KEY-----\nXXXXXXXXXX\n-----END PRIVATE KEY-----\n",
        "client_email": "XXXX-service-account@marcanuy-XXXXXX.iam.gserviceaccount.com",
        "client_id": "XXXX",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://accounts.google.com/o/oauth2/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/equilang-service-account%40marcanuy-XXXXX.iam.gserviceaccount.com"
    }
```

Once you retrieve your json, In the terminal, you set the whole json file as an enviromental variable:

```
    export GOOGLE_APPLICATION_CREDENTIALS="$(< name_of_json_file.json)"
```

If you call .env. You should see:

```
    echo $GOOGLE_APPLICATION_CREDENTIALS
    { "type": "service_account", "project_id": "marcanuy-XXXXX", "private_key_id": "XXXXXX", "private_key": "-----BEGIN PRIVATE KEY-----\nXXXXXX\n-----END PRIVATE KEY-----\n", "client_email": "equilang-service-account@marcanuy-XXXX.iam.gserviceaccount.com", "client_id": "XXXXXX", "auth_uri": "https://accounts.google.com/o/oauth2/auth", "token_uri": "https://accounts.google.com/o/oauth2/token", "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs", "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/equilang-service-account%40marcanuy-XXXXXXX.iam.gserviceaccount.com" }
```

Because GOOGLE_APPLICATION_CREDENTIALS is a string, we need to require it and convert it back to json. In views.py:

```Python
    import json
    from google.oauth2 import service_account
    from google.cloud import vision
    from google.cloud.vision import types

    credentials_raw = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')

    service_account_info = json.loads(credentials_raw)

    credentials = service_account.Credentials.from_service_account_info(service_account_info)
```

Now your credentials are available, you should test one of the scripts that Google provides

## Stripe payment API

To set up stripe payment, you'll need to create a stripe account and retrieve the API key

```Python
    STRIPE_PUBLIC_KEY = os.environ.get("STRIPE_SECRET_KEY", "pk_YOUR_TEST_PUBLIC_KEY")
    STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "pk_YOUR_TEST_SECRET_KEY")
```

Then we set up a function that will redirect us to the payment method on accepting the transaction

```python
    from yourapp import settings

    def payment_form(request):

        context = { "stripe_key": settings.STRIPE_PUBLIC_KEY }
        return render(request, "yourtemplate.html", context)
```

This will render a button on your template html and on click it will pop up a modal. Below we can see many fields were filled, so lets go over them. Data-ket is just the stripe key that was provided on the website, data-amount is the total price that will be charged, the last 2 digits are decimal places, finally, data-description, data-image, data-name are pretty intuitive.

```python
    <form action="/checkout" method="POST">
        <script src="https://checkout.stripe.com/checkout.js" class="stripe-button"
            data-key="stripe_key" # Make sure to wrap the variable name with double {}
            data-amount="2000"
            data-name="Your APp"
            data-description="Your Product"
            data-image="Link to your logo"
            data-currency="usd">
        </script>
    </form>

```

Set the url:

```python
    urls = [
        path("checkout", views.checkout, name="checkout")
    ]
```

On views.py, we write a function that will handle the payment and transaction

```python
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
        Total_price = sum(Total_price*100)
        return render(request, "couponBank/payment.html", { "stripe_key": settings.STRIPE_TEST_PUBLIC_KEY, "orders":orders, "Total_price":Total_price })

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
                    amount=100*Total_price,
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

```

## Models

This is the user profile model, which includes all information for the shipping as well as contact information

```Python
    class UserProfile(models.Model):
        user = models.OneToOneField(User,on_delete=models.CASCADE, related_name='profile')
        profile_pic = models.ImageField(upload_to='profile_pics',blank=True)
        phone = models.CharField(blank=True,max_length=50)
        country = CountryField(blank_label='(select country)',blank=True)
        address = models.CharField(blank=True,max_length=50)
        zipcode = models.CharField(blank=True,max_length=50)

        def __str__(self):
            return self.user.username
```

Product model represents an individual item that was posted by the user, and it's related by the foreign key

```Python
    class Product (models.Model):
        brand = models.CharField(max_length=1000,blank=True)
        description = models.TextField(max_length=1000,blank=True)
        picture = models.ImageField(upload_to='picture/',blank=True)
        posted_at = models.DateTimeField()
        price = models.PositiveIntegerField(blank=True)
        user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='products') #Many products to a user

        def __str__(self):
            return self.brand
```

Order represents the single item that was grabbed and put on the shopping cart

```Python
    class Order (models.Model): 
        ref_code = models.CharField(max_length=100)
        buyer = models.ForeignKey(User,on_delete=models.SET_NULL, null=True)
        is_ordered = models.BooleanField(default=False)
        products = models.ForeignKey(Product,on_delete=models.CASCADE,related_name='product') #Many products to an order
        date_ordered = models.DateTimeField()

        def __str__(self):
            return str(self.products)
```

Transaction is just the list of items that was bought and it's related to the Order class via many to many field.

```Python
    class Transaction (models.Model):
        profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
        token = models.CharField(max_length=120)
        orders = models.ManyToManyField(Order)
        amount = models.DecimalField(max_digits=100, decimal_places=2)
        success = models.BooleanField(default=True)
        timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)

        def __str__(self):
            return str(self.orders)
```

Finally, Reviews just represents all comments that are related to the product.

```Python
    class Reviews(models.Model):
        product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name='review')
        user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='review')
        title = models.CharField(max_length=50, blank=True)
        description = models.TextField(max_length=300, blank=True)
        post_date = models.DateTimeField(auto_now_add=True, auto_now=False)

        def __str__(self):
            return self.title
```

## Extra features to add

- Peer-to-peer trading: Implementation a mediator/middleman to handle the transaction
- Revenue: Make Stripe to take a small amount of the total transaction price as revenue for the website
- Watermark portection: As it's right now, nothing prevents other users from taking a photo to the coupon. Although django provides a watermark library, it only works on png files.
- Print Receipt: Another cool feature to add would be giving the user the option to print their purchases receipts on pdf format
