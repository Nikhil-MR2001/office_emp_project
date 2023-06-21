from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('all_emp', views.all_emp, name='all_emp'),
    path('add_emp', views.add_emp, name='add_emp'),
    path('remove_emp', views.remove_emp, name='remove_emp'),
    path('remove_emp/<int:id>', views.remove_emp, name='remove_emp'),
    path('filter_emp', views.filter_emp, name='filter_emp'),
    path('update/<int:id>', views.update_emp, name='update_emp'),

    path('msg', views.msg, name='msg'),
    path('shop', views.shop, name='shop'),

    path('login', views.login, name='login'),
    path('register/', views.register, name='register'),


    # E-commerce
    path('shop', views.shop, name='shop'),
    # path('shoplogin', views.shoplogin, name='shoplogin'),
    path('shopdetail/<int:id>', views.shopdetail, name='shopdetail'),


    path('cart', views.cart, name='cart'),
    path('add_to_cart/<int:id>', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<int:id>', views.remove_from_cart, name='remove_from_cart'),

    path('checkoutview', views.checkout_view, name='checkoutview'),
    path('create-checkout-session', views.create_checkout_session, name='create_checkout_session'),
]