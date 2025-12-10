from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path('',views.home,name="home"),
    path('accounts/login/',views.sigin,name="login"),
    path('signup/',views.sign_up,name="signup"),
    path('add_blog/',views.add_blog,name="add_blog"),
    path('gallery/',views.gallery,name="gallery"),
    path('logout/',views.user_logout,name="logout"),
    path('edit/<int:id>/',views.edit,name="edit"),
    path('delete/<int:id>/',views.delete,name="delete"),
    path('profile/',views.profile,name="profile"),
    path("forget_password",views.forget,name="forget"),
    path("search/",views.search,name="search"),
    path("edit_profile/<int:id>/",views.edit_profile,name="edit_profile")
]
