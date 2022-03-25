"""djangoProject URL Configuration
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from main import views


urlpatterns = [
    path('Admin', views.Admin, name='Admin'),
    path('', views.Home, name='Home'),
    path('Login', views.Login, name='Login'),
    path('Register',views.Register, name='Register'),
    path('placeOrder', views.placeOrder, name='placeOrder'),
    path('claimedOrder',views.claimedOrder, name='claimedOrder'),
    path('myOrder', views.myOrder, name='myOrder'),
    path('Profile', views.Profile, name='Profile'),
    path('View/<str:id>', views.View, name='View'),
    path('editUser/<str:id>', views.editUser, name='editUser'),
    path('editOrder/<str:id>', views.editOrder, name='editOrder'),
    path('try', views.tryy, name='Homee')
]
