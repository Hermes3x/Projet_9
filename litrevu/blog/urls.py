from django.urls import path
from . import views

app_name = "blog"

utlpatterns = [
    path('', views.home, name='home')
]
