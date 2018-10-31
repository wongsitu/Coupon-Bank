# Coupon Bank

Coupon Bank is a peer-to-peer lending aplication that allows users to buy and sell coupons. The motivation of this project was to create an exchange platform that would allow users to trade 'long tail' coupons. It offers most of the main functionalities of any trading website, the current design was heavily inspired by Amazon. To run this application,you will need to get Google credentials json file, a Stripe API Key and your AWS credentials. The set up for these are explained in the sections below.

Link: https://waikamazon.herokuapp.com/

## Images
Here are some images of my application

![Alt text](https://github.com/wongsitu/Coupon-Bank/blob/master/assets/homepage.png)

![Alt text](https://github.com/wongsitu/Coupon-Bank/blob/master/assets/coupon1.png)

![Alt text](https://github.com/wongsitu/Coupon-Bank/blob/master/assets/coupon2.png)

![Alt text](https://github.com/wongsitu/Coupon-Bank/blob/master/assets/aboutpage.png)

![Alt text](https://github.com/wongsitu/Coupon-Bank/blob/master/assets/post_product.png)

![Alt text](https://github.com/wongsitu/Coupon-Bank/blob/master/assets/FAQ.png)

![Alt text](https://github.com/wongsitu/Coupon-Bank/blob/master/assets/profilepage.png)

![Alt text](https://github.com/wongsitu/Coupon-Bank/blob/master/assets/offers.png)

![Alt text](https://github.com/wongsitu/Coupon-Bank/blob/master/assets/invoice_receipt.png)

## Features

- User authentication: Users are able to Log in, Log out and Register
- Google Cloud Vision API: When the users upload their coupons, GCVA will grab all the information from the coupon using visual recognition. This includdes the Logo and description. If the coupon is not valid, it will return an invalid message
- Stripe: Includes payment system that handles all transactions. It takes a pertentage of the total price as revenue for the website
- Amazon Website Services: Heroku will delete your media storage after 30 minutes if nobody requests your website, therefore we use AWS store them. 
- CRUD functionality: Users are able to create, read, update and delete reviews. Also they are able to create, read and delete coupons that were posted/ordered

## Technologies

- Front End: HTML, CSS, Bootstrap, Fontawesome
- Back End: Django 2.0+, Python 3.7.0, Javascript, jQuery
- APIs: Google Cloud API, Stripe
- Django modules: django countries, dj-stripe, Pillow, django-storage, boto3

## How to set Google Cloud Vision API

The hardest part of couponBank was to set up GCVA. First, You need to have a google account. Then you will have to go to https://cloud.google.com/vision/. Log in into your account and on the top left corner, click the hamburger.

You will need to give your credit/debit card details, but dont worry, Google won't charge you for your first year of usage. Also, you will be given $300 as credit for their services. Feel free to explore other Machine Learning APIs.

Once you got that done, click the hamburger menu again, and go to APIs and Services, hover your mouse on it and you'll see a  Dashboard option. Click on it. This will take you to another window and you'll need to create a project.

Then go to your credentials, and press the "create credentials". Create an API key and retrieve your Service Account key.

You will be able to retrieve an json file, which is your Service Account key, that contains all your credentials. It should look something like this:

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

Before continuing, we need to install some libraries.Do not close your Service Account key json file yet. In your terminal run the following commands: 

```
    pip3 install --upgrade google-api-python-client
    pip3 install --upgrade google-cloud-vision
    pip3 install --upgrade google-cloud
```
With everything installed, we need Google SDK, go to this link: https://cloud.google.com/sdk/docs/ and follow steps 1 though 5. You whould have a google-cloud-sdk folder installed by the end of step 4. At this point copy the folder and move it into your application file. In our case, we copied and pasted it in couponBank. DO NOT forget to gitignore it! it's a very heavy file so we don't wanna push it to our repo. 

If everything is good, in your terminal type the following command:

```
    gcloud auth login
```

This will open a window in your browser and will ask you to login to your Google account. After you log in, you will be able to use vision.Client, which is a way to authenticate your credentials.

Now back to working with our credentials, you should download it or keep it in a .env file. In the terminal, you have to set the whole json file as an enviromental variable:

```
    export GOOGLE_APPLICATION_CREDENTIALS="$(< name_of_credentials_json_file.json)"
```

If you call env in the terminal, You should see:

```
    echo $GOOGLE_APPLICATION_CREDENTIALS
    { "type": "service_account", "project_id": "marcanuy-XXXXX", "private_key_id": "XXXXXX", "private_key": "-----BEGIN PRIVATE KEY-----\nXXXXXX\n-----END PRIVATE KEY-----\n", "client_email": "equilang-service-account@marcanuy-XXXX.iam.gserviceaccount.com", "client_id": "XXXXXX", "auth_uri": "https://accounts.google.com/o/oauth2/auth", "token_uri": "https://accounts.google.com/o/oauth2/token", "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs", "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/equilang-service-account%40marcanuy-XXXXXXX.iam.gserviceaccount.com" }
```

Because GOOGLE_APPLICATION_CREDENTIALS is a string, we need to require it and convert it back to json. In views.py, we will need to import all modules that we need:

```Python
    import json
    from google.oauth2 import service_account
    from google.cloud import vision
    from google.cloud.vision import types

    credentials_raw = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')

    service_account_info = json.loads(credentials_raw)

    credentials = service_account.Credentials.from_service_account_info(service_account_info)
```

Now your credentials are available, you should test one of the scripts that Google provides. Take a look at this link: https://cloud.google.com/vision/docs/detecting-logos. In the sample section you will see many other image detection features, Feel free to test all scripts.

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

On views.py, we write a function that will handle the payment and transaction. NOTE: Stripe does not create any transactions, it only charges you money. Everything else has to be coded.

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
```

```python
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
                # We create the transaction once the payment is valid
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
## AWS Image Storage
Heroku is not very friendly with Django uploaded images, specially when using Pillow. If there are not any request to your site for 30 minutes, all images will be broken. Because of this, we have to use AWS storage along with boto3 and django-storages libraries. To set this up, you need to set up a bucket on Amazon Website Services. This will act as our new media folder.

In AWS dashboard, create an account and retrieve an AWS credentials. Download them since they are very important and set it into an enviromental variable. Follow me along these steps:

In terminal: 

```
    pip install boto3
    pip install django-storages
```
In settings.py add storages:

```python
    INSTALLED_APPS = [
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',

        'storages',
    ]
```

Create a new python file name storage_backends.py in the same level of settings.py. 

```python
    from storages.backends.s3boto3 import S3Boto3Storage

    class MediaStorage(S3Boto3Storage):
        location = 'media'
        file_overwrite = False
```

Then, add your AWS credentials:

```python
    AWS_ACCESS_KEY_ID = 'AKIAIT2Z5TDYPX3ARJBA'
    AWS_SECRET_ACCESS_KEY = 'qR+vjWPU50fCqQuUWbj9Fain/j2pV+ZtBCiDiieS'
    AWS_STORAGE_BUCKET_NAME = 'sibtc-assets'
    AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME

    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
    }
```
Do NOT push to GitHub like that, set it up to enviromental variables! For example, in terminal:

```
    export AWS_ACCESS_KEY_ID = 'AKIAIT2Z5TDYPX3ARJBA'
    export AWS_SECRET_ACCESS_KEY = 'qR+vjWPU50fCqQuUWbj9Fain/j2pV+ZtBCiDiieS'
    export AWS_STORAGE_BUCKET_NAME = 'sibtc-assets'
```
Now you can call them in your settings.py as:

```python
    AWS_ACCESS_KEY_ID = os.environ('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.environ('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME

    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
    }
```

Then in terminal:

```
    python manage.py collectstatic
```

This will create a staticfiles outside your application, move staticfiles inside app folder and write it on gitignore files. staticfiles are not the kind of files you might want to push up. Finally, since we are working with Google API vision cloud, we need to set our AWs bucket to public read because it now works as our media folder for Pillow. Assuming that you've set upt your AWS bucket and followed the instructions above, you should be able to upload images, which won't break on heroku deployment.

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
