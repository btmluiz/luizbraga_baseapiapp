from django.urls import path

from luizbraga_baseapi import views

urlpatterns = [
    path('login/', views.LoginAuthToken.as_view()),
]
