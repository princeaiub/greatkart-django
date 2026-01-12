"""
URL configuration for greatkart project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from pages.views import *
from staff_portal.views import *
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('',home, name='home'),
    path('store/', store, name='store'),
    path('store/<str:cat_name>/', all_product_under_category_of_store, name='all_product_under_category_of_store'),
    path('store/<str:cat_name>/<str:product_slug>', single_product_details, name='single_product_details'),
    path('cart/', cart, name='cart'),
    path('cart/<int:product_id>/' ,add_cart,name='add_cart'),
    # path('cart/increase_product/<int:product_id>', add_cart, name='increase_product'),
    path('cart/decrease_product/<int:product_id>', decrease_product, name='decrease_product'),
    path('cart/remove_product/<int:product_id>', remove_product, name='remove_product'),
    # path of staff_portal
    path('BrowserWeb/staff/login/',staff_login, name='login'),
    path('BrowserWeb/staff/staff_home/', staff_home, name = 'staff_home'),
    path('BrowserWeb/staff/add_user/', add_user, name= 'add_user'),
    path('BrowserWeb/staff/all_users/', all_users, name= 'all_users'),
    path('BrowserWeb/staff/edit_staff_users/<int:user_id>/', edit_staff_users, name='edit_staff_users'),
    path('BrowserWeb/staff/all_user_search/',all_user_search, name='all_user_search'),
    path('BrowserWeb/staff/sign_out/',sign_out, name='sign_out'),
    path('BrowserWeb/staff/change_password_for_activation/', change_password_for_activation, name='change_password_for_activation'),
    path('BrowserWeb/staff/change_password/',change_password, name='change_password'),
    path('BrowserWeb/staff/all_category/',all_category,name='all_category'),
    path('BrowserWeb/staff/add_category/',add_category,name='add_category'),
    path('BrowserWeb/staff/all_product_under_cat/<int:cat_id>/',all_product_under_cat,name='all_product_under_cat'),
    path('BrowserWeb/staff/add_product/',add_product,name='add_product'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)