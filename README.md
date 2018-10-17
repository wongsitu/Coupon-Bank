# Coupon Bank

Coupon Bank is a peer-to-peer lending aplication that allows users to buy and sell coupons. The motivation of this project was to create an exchange platform that would allow users to trade 'long tail' coupons.

## Features

- User authentication: Users are able to Log in, Log out and Register
- Google Cloud Vision API: When the users upload their coupons, GCVA will grab all the information from the coupon using visual recognition. This includdes the Logo and description
- Stripe: Includes payment system that handles all transactions
- CRUD functionality: Users are able to create, read, update and delete reviews. Also they are able to create, read and delete coupons that were posted/ordered

## Technologies

- Front End: HTML, CSS, Bootstrap, Fontawesome
- Back End: Django 2.0+, Python 3.7.0, Javascript, jQuery
- APIs: Google Cloud API, Stripe
- Django modules: django countries, dj-stripe, Pillow

## Google Cloud Vision API

The hardest part of couponBank was to set up GCVA. First, You need to have a google account. Then you go to https://console.cloud.google.com/ and create a new project. You will be able to retrieve an json file that contains all your credentials. It should look something like this:

```
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

```
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

## Models

This is the user profile model, which includes all information for the shipping as well as contact information

```
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

```
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

```
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

```
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

```
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
