# simple/urls.py
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('help', views.question, name='question'),
    path('<str:room_name>/', views.room, name='room'),
]
