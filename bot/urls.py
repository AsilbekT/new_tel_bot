from django.urls import path
from . import views

urlpatterns = [
    path('setwebhook/', views.setwebhook),
    path('', views.index),
    path('getpost/', views.getpost)
]
