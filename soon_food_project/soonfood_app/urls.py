"""soon_food_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index),
    path('food/', views.food),
    path('df_btn/', views.df_btn_click),
    path('food/df_btn/', views.df_btn_click),
    path('random_choice/', views.random_cate),
    path('search_food/', views.search_food_btn),
    path('random_choice/select_detail/', views.detail_content),
    path('search_food/select_detail/', views.detail_content),
    path('food/menu/', views.menu_lst),
    path('food/check_food/', views.check_food),
    path('random_choice/menu/', views.menu_lst),
    path('random_choice/select_detail/menu/', views.menu_lst),
    path('food/select_detail/', views.detail_content),
    path('search_food/menu/', views.menu_lst),
    path('random_choice/select_food/', views.select_food),
    path('random_choice/select_food_btn/', views.select_food),
    path('/select_food_btn/', views.select_food)



    # path('random_choice/detail_contents1/', views.detail_content),
    # path('random_choice/check_food/', views.detail_content),
    # path('random_choice/detail_contents3/', views.detail_content)
]
