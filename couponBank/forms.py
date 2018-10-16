from django import forms
from .models import UserProfile, Product, Order, Reviews
from django.contrib.auth.models import User

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    class Meta():
        model = User
        fields = ('username','password','email')

class UserProfileForm(forms.ModelForm):
    class Meta():
        model = UserProfile
        fields = ('profile_pic', 'phone','country','address','zipcode')

class ProductForm(forms.ModelForm):
    class Meta():
        model = Product
        fields = ('picture', 'price')

class ReviewForm(forms.ModelForm):
    class Meta():
        model = Reviews
        fields = ('title','description')
