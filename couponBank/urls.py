from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.homepage, name="homepage"),
    path('about', views.about, name='about'),
    path('FAQ', views.FAQ, name='FAQ'),
    path('register', views.register, name='register'),
    path('login', views.user_login, name="user_login"),
    path('logout', views.user_logout, name='logout'),
    path('profile', views.profile, name='profile'),
    path('profile/edit_profile', views.edit_profile, name='edit_profile'),
    path('profile/shoppingCart', views.shoppingCart, name='shoppingCart'),
    path('checkout', views.checkout, name='checkout'),
    path('create_product', views.create_product, name='create_product'),
    path('search', views.search, name='search'),

    path('product/<int:pk>', views.product_detail, name="product_detail"),
    path('delete_product/<int:pk>', views.delete_product, name="delete_product"),

    path('add_to_cart/<int:pk>', views.add_to_cart, name='add_to_cart'),
    path('delete_from_cart/<int:pk>', views.delete_from_cart, name="delete_from_cart"),
    path('detele_transaction/<int:pk>', views.detele_transaction, name="detele_transaction"),
    path('payment', views.payment, name='payment'),
    path('invoice/<int:pk>', views.invoice, name="invoice"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)