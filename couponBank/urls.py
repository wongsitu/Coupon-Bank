from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.homepage, name="homepage"),
    path('register', views.register, name='register'),
    path('login', views.user_login, name="user_login"),
    path('logout', views.user_logout, name='logout'),
    path('profile', views.profile, name='profile'),
    path('about', views.about, name='about'),
    path('shoppingCart', views.shoppingCart, name='shoppingCart'),
    path('create_product', views.create_product, name='create_product'),
    path('FAQ', views.FAQ, name='FAQ'),
    path('product/<int:pk>', views.product_detail, name="product_detail"),
    path('payment', views.payment, name='payment'),
    # path("checkout", views.checkout, name="checkout")
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)